"""Index = chunks + BM25 (keyword) + dense vectors, persisted to disk.

Vector store choice: an exact (brute-force) cosine search over a NumPy matrix.
For a hackathon-sized corpus (<200k chunks) this is as fast as FAISS FlatIP,
has zero install pain, and gives *exact* nearest neighbours. Scaling path:
swap `DenseStore` for Chroma / pgvector / Qdrant (same interface: add, search).
"""
from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

import numpy as np

from .arabic import tokenize
from .embeddings import Embedder, TfidfEmbedder, make_embedder
from .ingest import Chunk


class BM25:
    """Okapi BM25 (k1=1.5, b=0.75) over Arabic-normalised, light-stemmed tokens."""

    def __init__(self, docs_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(t) for t in docs_tokens]
        self.len = np.array([len(t) for t in docs_tokens], dtype=np.float32)
        self.avg = float(self.len.mean()) if len(self.len) else 0.0
        df = Counter()
        for t in docs_tokens:
            df.update(set(t))
        n = len(docs_tokens)
        self.idf = {w: math.log(1 + (n - f + 0.5) / (f + 0.5)) for w, f in df.items()}
        # inverted index for speed
        self.postings: dict[str, list[int]] = {}
        for i, c in enumerate(self.tf):
            for w in c:
                self.postings.setdefault(w, []).append(i)

    def scores(self, q_tokens: list[str]) -> np.ndarray:
        s = np.zeros(len(self.tf), dtype=np.float32)
        for w in set(q_tokens):
            idf = self.idf.get(w)
            if idf is None:
                continue
            for i in self.postings[w]:
                f = self.tf[i][w]
                denom = f + self.k1 * (1 - self.b + self.b * self.len[i] / (self.avg or 1))
                s[i] += idf * f * (self.k1 + 1) / denom
        return s


class Index:
    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.chunks: list[Chunk] = []
        self.bm25: BM25 | None = None
        self.embedder: Embedder | None = None
        self.vectors = None
        self.info: dict = {}

    # ------------------------------------------------------------------ build
    @staticmethod
    def search_text(c: Chunk) -> str:
        """What we index: contextual header + passage (improves recall a lot)."""
        return f"{c.header()}\n{c.text}"

    def build(self, chunks: list[Chunk], settings) -> "Index":
        t0 = time.time()
        self.chunks = chunks
        texts = [self.search_text(c) for c in chunks]
        self.bm25 = BM25([tokenize(t) for t in texts])
        self.embedder = make_embedder(settings)
        self.embedder.fit(texts)
        self.vectors = self.embedder.embed_docs(texts) if texts else None
        self.info = {"embedder": self.embedder.name, "chunks": len(chunks),
                     "sources": sorted({c.source for c in chunks}),
                     "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                     "build_seconds": round(time.time() - t0, 2)}
        return self

    def save(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "chunks.json").write_text(
            json.dumps([c.to_dict() for c in self.chunks], ensure_ascii=False), encoding="utf-8")
        (self.folder / "info.json").write_text(json.dumps(self.info, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
        if isinstance(self.embedder, TfidfEmbedder):
            self.embedder.save(self.folder)
        elif self.vectors is not None:
            np.save(self.folder / "vectors.npy", self.vectors)

    # ------------------------------------------------------------------ load
    def load(self, settings) -> "Index":
        data = json.loads((self.folder / "chunks.json").read_text(encoding="utf-8"))
        self.chunks = [Chunk(**d) for d in data]
        self.info = json.loads((self.folder / "info.json").read_text(encoding="utf-8"))
        texts = [self.search_text(c) for c in self.chunks]
        self.bm25 = BM25([tokenize(t) for t in texts])
        backend = self.info.get("embedder", "tfidf").split(":")[0]
        if backend == "tfidf":
            self.embedder = TfidfEmbedder()
            self.embedder.load(self.folder)
            self.vectors = self.embedder.embed_docs(texts) if texts else None
        else:
            self.embedder = make_embedder(settings, prefer=backend)
            if self.embedder.name.startswith("tfidf"):        # backend unavailable now
                self.embedder.fit(texts)
                self.vectors = self.embedder.embed_docs(texts)
                self.info["embedder"] = self.embedder.name
            else:
                self.vectors = np.load(self.folder / "vectors.npy")
        return self

    @classmethod
    def exists(cls, folder: Path) -> bool:
        return (Path(folder) / "chunks.json").exists()

    # ------------------------------------------------------------------ search
    def dense_scores(self, query: str) -> np.ndarray:
        if self.vectors is None:
            return np.zeros(0, dtype=np.float32)
        q = self.embedder.embed_query(query)
        if hasattr(self.vectors, "tocsr"):                     # sparse tf-idf
            return np.asarray((self.vectors @ q.T).toarray()).ravel().astype(np.float32)
        return (self.vectors @ q).astype(np.float32)

    def bm25_scores(self, query: str) -> np.ndarray:
        return self.bm25.scores(tokenize(query)) if self.bm25 else np.zeros(0)
