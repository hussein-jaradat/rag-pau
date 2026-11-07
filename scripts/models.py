"""python -m scripts.models -> models.txt : which models this account can use (no secrets printed)"""
import json, urllib.request
from rag.config import settings as s
out = []
def get(url, headers):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PalUniv-RAG-Advisor/1.0)", **headers})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
try:
    d = get("https://api.groq.com/openai/v1/models", {"Authorization": f"Bearer {s.groq_key}"})
    out.append("GROQ: " + ", ".join(sorted(m["id"] for m in d.get("data", []))))
except Exception as e:
    out.append(f"GROQ list failed: {e}")
try:
    d = get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", {"x-goog-api-key": s.gemini_key})
    out.append("GEMINI: " + ", ".join(sorted(m["name"].split("/")[-1] for m in d.get("models", [])
                                              if "generateContent" in m.get("supportedGenerationMethods", []))))
except Exception as e:
    out.append(f"GEMINI list failed: {e}")
open("models.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
