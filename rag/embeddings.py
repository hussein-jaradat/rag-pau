"""Pluggable embedding backends. All return L2-normalised float32 matrices.

  local  : sentence-transformers multilingual model (default intfloat/multilingual-e5-small,
           strong on Arabic, free, runs offline on CPU). Use BAAI/bge-m3 for best quality.
  openai : text-embedding-3-small (cheap, very good multilingual)
  gemini : Google text-embedding-004 (free tier)
  tfidf  : character n-gram TF-IDF (no download, no key; robust to Arabic morphology).
           A safety net so the demo never dies.
  auto   : first one that works: local -> openai -> gemini -> tfidf
"""
from __future__ import annotations

import json
import pickle
import urllib.request
from pathlib import Path

import numpy as np

from .arabic import normalize


def _l2(m: np.ndarray) -> np.ndarray:
    m = np.asarray(m, dtype=np.float32)
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n[n == 0] = 1
    return m / n


class Embedder:
    name = "base"

    def fit(self, texts: list[str]) -> None:  # only tfidf needs fitting
        pass

    def embed_docs(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_docs([text])[0]

    def save(self, folder: Path) -> None:
        pass

    def load(self, folder: Path) -> None:
        pass


class LocalEmbedder(Embedder):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # noqa: raises ImportError if missing

        self.model_name = model_name
        self.name = f"local:{model_name}"
        self.model = SentenceTransformer(model_name)
        self.e5 = "e5" in model_name.lower()

    def embed_docs(self, texts):
        if self.e5:
            texts = [f"passage: {t}" for t in texts]
        return _l2(self.model.encode(texts, batch_size=32, show_progress_bar=len(texts) > 64,
                                     normalize_embeddings=True))

    def embed_query(self, text):
        q = f"query: {text}" if self.e5 else text
        return _l2(self.model.encode([q], normalize_embeddings=True))[0]


def _post(url: str, payload: dict, headers: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (PalUniv-RAG-Advisor/1.0)", "Accept": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


class OpenAIEmbedder(Embedder):
    def __init__(self, key: str, model: str, base_url: str):
        if not key:
            raise ValueError("OPENAI_API_KEY missing")
        self.key, self.model, self.base = key, model, base_url.rstrip("/")
        self.name = f"openai:{model}"

    def embed_docs(self, texts):
        out = []
        for i in range(0, len(texts), 96):
            data = _post(f"{self.base}/embeddings", {"model": self.model, "input": texts[i:i + 96]},
                         {"Authorization": f"Bearer {self.key}"})
            out.extend(d["embedding"] for d in data["data"])
        return _l2(np.array(out))


class GeminiEmbedder(Embedder):
    def __init__(self, key: str, model: str):
        if not key:
            raise ValueError("GEMINI_API_KEY missing")
        self.key, self.model = key, model
        self.name = f"gemini:{model}"

    def _batch(self, texts, task):
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}"
               f":batchEmbedContents?key={self.key}")
        reqs = [{"model": f"models/{self.model}", "content": {"parts": [{"text": t}]},
                 "taskType": task} for t in texts]
        return [e["values"] for e in _post(url, {"requests": reqs}, {})["embeddings"]]

    def embed_docs(self, texts):
        out = []
        for i in range(0, len(texts), 100):
            out.extend(self._batch(texts[i:i + 100], "RETRIEVAL_DOCUMENT"))
        return _l2(np.array(out))

    def embed_query(self, text):
        return _l2(np.array(self._batch([text], "RETRIEVAL_QUERY")))[0]


class TfidfEmbedder(Embedder):
    """Char 2-5 grams on normalised text. Not 'semantic', but surprisingly strong
    for Arabic (handles prefixes/suffixes) and needs nothing."""
    name = "tfidf:char2-5"

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1,
                                   sublinear_tf=True, preprocessor=normalize, max_features=200_000)
        self.fitted = False

    def fit(self, texts):
        self.vec.fit(texts)
        self.fitted = True

    def embed_docs(self, texts):
        if not self.fitted:
            self.fit(texts)
        return self.vec.transform(texts)  # sparse, already l2-normalised

    def embed_query(self, text):
        return self.vec.transform([text])

    def save(self, folder):
        with open(folder / "tfidf.pkl", "wb") as f:
            pickle.dump(self.vec, f)

    def load(self, folder):
        with open(folder / "tfidf.pkl", "rb") as f:
            self.vec = pickle.load(f)
        self.fitted = True


def make_embedder(s, prefer: str | None = None) -> Embedder:
    choice = (prefer or s.embedder).lower()
    order = ["local", "openai", "gemini", "tfidf"] if choice == "auto" else [choice]
    errors = []
    for c in order:
        try:
            if c == "local":
                return LocalEmbedder(s.local_embed_model)
            if c == "openai":
                return OpenAIEmbedder(s.openai_key, s.openai_embed_model, s.openai_base_url)
            if c == "gemini":
                return GeminiEmbedder(s.gemini_key, s.gemini_embed_model)
            if c == "tfidf":
                return TfidfEmbedder()
        except Exception as e:  # missing package / key -> try the next one
            errors.append(f"{c}: {e.__class__.__name__}: {e}")
    if choice != "auto":
        print("[embed] requested backend failed -> falling back to tfidf:", errors)
        return TfidfEmbedder()
    raise RuntimeError("No embedder available: " + "; ".join(errors))
