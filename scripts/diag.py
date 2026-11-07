"""python -m scripts.diag  -> writes diag.txt (no secrets)"""
import os, traceback
from rag.config import settings as s
from rag.llm import LLM
out = [f"provider={s.llm_provider} model={s.default_model()} fast={s.fast_model()} fallback={s.fallback_provider}:{s.fallback_model}",
       f"groq_key_len={len(s.groq_key)} gemini_key_len={len(s.gemini_key)}",
       f"env overrides: LLM_PROVIDER in os.environ before dotenv? {os.environ.get('LLM_PROVIDER')}"]
llm = LLM(s)
out.append(f"available={llm.available}")
for m in [s.default_model(), s.fast_model()]:
    try:
        r = llm._complete_one(s.llm_provider, "Reply with one word.", [{"role": "user", "content": "قل مرحبا"}], m, 20, 0, False)
        out.append(f"OK {m}: {r.text!r} ({r.seconds}s)")
    except Exception as e:
        out.append(f"FAIL {m}: {str(e)[:500]}")
open("diag.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
