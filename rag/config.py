"""Central configuration. Everything is read from environment variables (.env),
so no secret ever lives in the code. Change behaviour without touching code."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass
class Settings:
    # ---- domain / problem ------------------------------------------------
    domain: str = field(default_factory=lambda: _env("DOMAIN", "academic"))
    docs_dir: Path = field(default_factory=lambda: ROOT / _env("DOCS_DIR", "data/docs"))
    index_dir: Path = field(default_factory=lambda: ROOT / _env("INDEX_DIR", "storage/index"))
    db_path: Path = field(default_factory=lambda: ROOT / _env("DB_PATH", "storage/app.db"))

    # ---- chunking --------------------------------------------------------
    chunk_size: int = field(default_factory=lambda: int(_env("CHUNK_SIZE", "900")))      # characters
    chunk_overlap: int = field(default_factory=lambda: int(_env("CHUNK_OVERLAP", "150")))

    # ---- retrieval -------------------------------------------------------
    # embedder: auto | local | openai | gemini | tfidf
    embedder: str = field(default_factory=lambda: _env("EMBEDDER", "auto"))
    local_embed_model: str = field(
        default_factory=lambda: _env("LOCAL_EMBED_MODEL", "intfloat/multilingual-e5-small"))
    openai_embed_model: str = field(
        default_factory=lambda: _env("OPENAI_EMBED_MODEL", "text-embedding-3-small"))
    gemini_embed_model: str = field(
        default_factory=lambda: _env("GEMINI_EMBED_MODEL", "text-embedding-004"))
    retrieval_mode: str = field(default_factory=lambda: _env("RETRIEVAL_MODE", "hybrid"))  # bm25|dense|hybrid
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "5")))
    candidates: int = field(default_factory=lambda: int(_env("CANDIDATES", "20")))
    rerank: str = field(default_factory=lambda: _env("RERANK", "none"))  # none | llm | cross
    # refusal gate: minimum normalised relevance of the best chunk (0..1)
    min_relevance: float = field(default_factory=lambda: float(_env("MIN_RELEVANCE", "0.18")))
    query_rewrite: bool = field(default_factory=lambda: _env("QUERY_REWRITE", "1") == "1")

    # ---- generation ------------------------------------------------------
    # llm_provider: anthropic | openai | gemini | ollama | offline
    llm_provider: str = field(default_factory=lambda: _env("LLM_PROVIDER", "anthropic"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", ""))
    llm_fast_model: str = field(default_factory=lambda: _env("LLM_FAST_MODEL", ""))
    openai_base_url: str = field(
        default_factory=lambda: _env("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    fallback_provider: str = field(default_factory=lambda: _env("FALLBACK_PROVIDER", ""))
    fallback_model: str = field(default_factory=lambda: _env("FALLBACK_MODEL", ""))
    ollama_url: str = field(default_factory=lambda: _env("OLLAMA_URL", "http://localhost:11434"))
    max_tokens: int = field(default_factory=lambda: int(_env("MAX_TOKENS", "2048")))
    temperature: float = field(default_factory=lambda: float(_env("TEMPERATURE", "0.1")))

    # ---- keys (never logged) ----------------------------------------------
    anthropic_key: str = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    openai_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    gemini_key: str = field(default_factory=lambda: _env("GEMINI_API_KEY"))
    groq_key: str = field(default_factory=lambda: _env("GROQ_API_KEY"))

    # ---- app ---------------------------------------------------------------
    secret_key: str = field(default_factory=lambda: _env("SECRET_KEY", "change-me-in-.env"))
    admin_user: str = field(default_factory=lambda: _env("ADMIN_USER", "admin"))
    admin_password: str = field(default_factory=lambda: _env("ADMIN_PASSWORD", "admin123"))
    port: int = field(default_factory=lambda: int(_env("PORT", "8000")))

    # rough prices (USD per 1M tokens) used for the live cost meter; override in .env
    price_in: float = field(default_factory=lambda: float(_env("PRICE_IN_PER_M", "2.0")))
    price_out: float = field(default_factory=lambda: float(_env("PRICE_OUT_PER_M", "10.0")))

    def default_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        return {
            "anthropic": "claude-sonnet-5-5",
            "openai": "gpt-4o-mini",
            "gemini": "gemini-3.8-flash",
            "groq": "qwen/qwen3.8-27b",
            "ollama": "qwen2.5:7b",
        }.get(self.llm_provider, "offline")

    def fast_model(self) -> str:
        if self.llm_fast_model:
            return self.llm_fast_model
        if self.llm_provider == "anthropic":
            return "claude-haiku-5-5"
        if self.llm_provider == "gemini":
            return self.default_model()
        if self.llm_provider == "groq":
            return "llama-3.1-8b-instant"
        return self.default_model()


settings = Settings()
