"""Rebuild the index from data/docs and write a readable report (UTF-8) to storage/ingest_report.txt
    python -m scripts.build_index
"""
import json
from collections import Counter

from rag.config import settings
from rag.pipeline import RAG

rag = RAG(auto_build=False)
rep = rag.rebuild()
kinds = Counter(c.kind for c in rag.index.chunks)
lines = [f"embedder: {rep.get('embedder')}", f"chunks: {rep['total_chunks']}  kinds: {dict(kinds)}",
         f"duplicates removed: {rep['duplicates_removed']}", f"skipped: {rep['skipped']}", "", "FILES:"]
lines += [f"  {f['file']}: pages={f['pages']} chunks={f['chunks']} tables={f['tables']} chars={f['chars']}"
          for f in rep["files"]]
lines += ["", "SAMPLE CHUNKS:"]
seen = set()
for c in rag.index.chunks:
    if c.source in seen:
        continue
    seen.add(c.source)
    lines.append(f"\n### {c.source} | p.{c.page} | {c.kind} | {c.section}\n{c.text[:400]}")
out = settings.index_dir.parent / "ingest_report.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"OK: {rep['total_chunks']} chunks from {len(rep['files'])} files -> report: {out}")
