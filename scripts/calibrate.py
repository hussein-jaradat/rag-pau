"""Find the best refusal threshold for YOUR documents (judges ask how you chose it).
    python -m scripts.calibrate
Prints the best-chunk similarity for answerable vs. unanswerable test questions."""
import json
from pathlib import Path
from rag.pipeline import RAG

rag = RAG()
tests = json.loads(Path("eval/testset_paluniv.json").read_text(encoding="utf-8"))
ins, oos = [], []
lines = []
for t in tests:
    hits = rag.retrieve([t["q"]])
    top = max((h.dense for h in hits), default=0)
    (oos if t.get("refuse") else ins).append(top)
    lines.append(f"{'OUT ' if t.get('refuse') else 'IN  '} {top:.3f}  {t['q']}")
lines.sort(key=lambda l: l.split()[1])
lo_in, hi_out = min(ins), max(oos)
sug = round((sorted(ins)[max(0, len(ins) // 10)] + hi_out) / 2, 3)
lines += ["", f"answerable: min={lo_in:.3f}   unanswerable: max={hi_out:.3f}",
          f"suggested GATE threshold for {rag.index.info['embedder']}: {sug}"]
Path("calibration.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[-2:]), "\n-> calibration.txt")
