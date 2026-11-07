"""One swappable function to talk to any LLM (as taught in Session 2), now with
providers: anthropic | openai (or any OpenAI-compatible: Groq, OpenRouter, Together)
| gemini | ollama (free local model) | offline (extractive fallback, no model).

Uses only the standard library, so there is nothing extra to install.
Returns text + token usage so we can show the cost of every answer.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class LLMResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    seconds: float = 0.0


def _post(url, payload, headers, timeout=90, retries=2):
    """POST with automatic retry on rate limits (free tiers allow only a few requests/minute)."""
    data = json.dumps(payload).encode()
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (PalUniv-RAG-Advisor/1.0)", "Accept": "application/json", **headers})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")[:400]
            if e.code in (429, 500, 503) and attempt < retries:
                try:
                    wait = float(e.headers.get("retry-after") or 0) + 1
                except ValueError:
                    wait = 0
                wait = wait if 3 <= wait < 60 else 4 * (attempt + 1)
                print(f"[llm] HTTP {e.code} (rate limit / busy) -> retry in {wait}s")
                time.sleep(wait)
                continue
            raise RuntimeError(f"LLM HTTP {e.code}: {body}") from None
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(3)
                continue
            raise RuntimeError(f"LLM network error: {e}") from None


class LLM:
    def __init__(self, settings):
        self.s = settings
        self.provider = settings.llm_provider.lower()

    @property
    def available(self) -> bool:
        p, s = self.provider, self.s
        return {"anthropic": bool(s.anthropic_key), "openai": bool(s.openai_key),
                "gemini": bool(s.gemini_key), "groq": bool(s.groq_key), "ollama": True}.get(p, False)

    def complete(self, system: str, messages: list[dict], model: str | None = None,
                 max_tokens: int | None = None, temperature: float | None = None,
                 json_mode: bool = False) -> LLMResult:
        """Primary provider first; if it is overloaded / rate-limited / down, automatically
        fall back to FALLBACK_PROVIDER (e.g. Groq Llama 3.3 70B) so the demo never stops."""
        try:
            return self._complete_one(self.provider, system, messages, model, max_tokens, temperature, json_mode)
        except Exception as e:
            fb = self.s.fallback_provider
            if not fb or fb == self.provider:
                raise
            print(f"[llm] {self.provider} failed ({str(e)[:60]}) -> fallback {fb}:{self.s.fallback_model}")
            r = self._complete_one(fb, system, messages, self.s.fallback_model or None,
                                   min(max_tokens or self.s.max_tokens, 800), temperature, json_mode)
            r.model = f"{fb}:{r.model} (fallback)"
            return r

    def _complete_one(self, p: str, system: str, messages: list[dict], model: str | None,
                      max_tokens: int | None, temperature: float | None, json_mode: bool) -> LLMResult:
        model = model or (self.s.default_model() if p == self.provider else "")
        max_tokens = max_tokens or self.s.max_tokens
        temperature = self.s.temperature if temperature is None else temperature
        t0 = time.time()
        if p == "anthropic":
            data = _post("https://api.anthropic.com/v1/messages",
                         {"model": model, "max_tokens": max_tokens, "temperature": temperature,
                          "system": system, "messages": messages},
                         {"x-api-key": self.s.anthropic_key, "anthropic-version": "2023-06-01"})
            text = "".join(b.get("text", "") for b in data.get("content", []))
            u = data.get("usage", {})
            res = LLMResult(text, u.get("input_tokens", 0), u.get("output_tokens", 0), model)
        elif p in ("openai", "ollama", "groq"):
            base = {"openai": self.s.openai_base_url, "groq": "https://api.groq.com/openai/v1",
                    "ollama": self.s.ollama_url.rstrip("/") + "/v1"}[p]
            payload = {"model": model, "max_tokens": max_tokens, "temperature": temperature,
                       "messages": [{"role": "system", "content": system}, *messages]}
            if json_mode and p in ("openai", "groq"):
                payload["response_format"] = {"type": "json_object"}
            key = {"openai": self.s.openai_key, "groq": self.s.groq_key}.get(p) or "ollama"
            headers = {"Authorization": f"Bearer {key}"}
            if "qwen" in model.lower():          # Qwen3: disable the long "thinking" block
                payload["messages"][0]["content"] += "\n/no_think"
            data = _post(base.rstrip("/") + "/chat/completions", payload, headers)
            u = data.get("usage", {}) or {}
            res = LLMResult(data["choices"][0]["message"]["content"] or "",
                            u.get("prompt_tokens", 0), u.get("completion_tokens", 0), model)
        elif p == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            contents = [{"role": "model" if m["role"] == "assistant" else "user",
                         "parts": [{"text": m["content"]}]} for m in messages]
            cfg = {"maxOutputTokens": max_tokens, "temperature": temperature}
            if "2.5" in model:                       # turn off "thinking": faster, no hidden token cost
                cfg["thinkingConfig"] = {"thinkingBudget": 0}
            if json_mode:
                cfg["responseMimeType"] = "application/json"
            data = _post(url, {"systemInstruction": {"parts": [{"text": system}]},
                               "contents": contents, "generationConfig": cfg},
                         {"x-goog-api-key": self.s.gemini_key})   # header works for AIza... and AQ... keys
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            u = data.get("usageMetadata", {})
            res = LLMResult("".join(x.get("text", "") for x in parts),
                            u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0), model)
        else:
            raise RuntimeError("offline provider has no model; caller should use extractive mode")
        res.text = re.sub(r"<think>.*?</think>", "", res.text, flags=re.S).strip()
        res.seconds = round(time.time() - t0, 2)
        return res

    def cost(self, r: LLMResult) -> float:
        return round(r.input_tokens / 1e6 * self.s.price_in + r.output_tokens / 1e6 * self.s.price_out, 6)


def parse_json(text: str):
    """Tolerant JSON extraction from an LLM reply."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("\n") + 1:] if "\n" in text else text
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("no json")
    end = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[start:end + 1])
