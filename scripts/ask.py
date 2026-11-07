"""Ask questions and write answers to answers.txt (UTF-8, readable in Notepad).
    python -m scripts.ask "سؤال 1" "سؤال 2"
"""
import sys
from rag.pipeline import RAG

rag = RAG()
out = []
history = []
for q in sys.argv[1:] or ["كم ساعة معتمدة أقدر أسجل بالفصل؟"]:
    a = rag.ask(q, history=history)
    history += [{"role": "user", "content": q}, {"role": "assistant", "content": a.answer}]
    out.append(f"Q: {q}\nrewritten: {a.standalone_query}\nrefused={a.refused} confidence={a.confidence} "
               f"time={a.timings.get('total')}s\n\n{a.answer}\n")
    for c in a.citations:
        out.append(f"  [{c['n']}] {c['title']} ({c['source']}) p.{c['page']} - {c['section']}  {c['url']}")
    out.append("\n" + "=" * 70 + "\n")
open("answers.txt", "w", encoding="utf-8").write("\n".join(out))
print("written answers.txt")
