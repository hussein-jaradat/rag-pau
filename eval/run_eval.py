"""Evaluation harness (judging criterion 1.4 + tie-breaker #2).

    python -m eval.run_eval                 # full eval with current .env settings
    python -m eval.run_eval --compare       # bm25 vs dense vs hybrid, k = 1/3/5 (before/after table)
    python -m eval.run_eval --retrieval-only

Metrics
  Retrieval : Hit@k (= Recall@k for one gold passage), Precision@k, MRR
  Answer    : keyword accuracy, refusal accuracy (out-of-scope refused / in-scope answered),
              citation accuracy (a cited source is a gold source)
  Grounding : Faithfulness = share of answer sentences supported by the retrieved context
              (LLM judge when a model is configured, lexical support check otherwise)
  Ops       : latency avg / p95, cost per answer
Outputs eval/report.md (paste it in the slides) + eval/results.json + error analysis.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import time
from copy import copy
from pathlib import Path

from rag.arabic import normalize, tokenize
from rag.config import settings
from rag.llm import parse_json
from rag.pipeline import RAG

HERE = Path(__file__).parent
NO_JUDGE = False
PACE = 0


def is_relevant(cite: dict, t: dict) -> bool:
    gold = t.get("gold_sources", [])
    if "*" not in gold and cite["source"] not in gold:
        return False
    needles = t.get("gold_contains") or []
    if not needles:
        return True
    text = normalize(cite["snippet"] + " " + (cite.get("section") or ""))
    return any(normalize(n) in text for n in needles)


def retrieval_metrics(rag: RAG, tests: list[dict], k: int, mode: str) -> dict:
    in_scope = [t for t in tests if not t.get("refuse")]
    hit = prec = rr = 0.0
    misses = []
    for t in in_scope:
        variants, _ = rag.understand(t["q"], t.get("history", []))
        hits = rag.retrieve(variants, k=k, mode=mode)
        rel = [is_relevant(h.cite(i + 1), t) for i, h in enumerate(hits)]
        hit += any(rel)
        prec += sum(rel) / k
        first = next((i for i, r in enumerate(rel) if r), None)
        rr += 1 / (first + 1) if first is not None else 0
        if first is None:
            misses.append(t["id"])
    n = len(in_scope) or 1
    return {"mode": mode, "k": k, "hit@k": round(hit / n, 3), "precision@k": round(prec / n, 3),
            "mrr": round(rr / n, 3), "misses": misses}


def lexical_faithfulness(answer: str, context: str) -> float:
    sents = [s for s in re.split(r"(?<=[\.\!\?؟])\s+|\n", re.sub(r"\[\d+\]", "", answer))
             if len(tokenize(s)) >= 3]
    if not sents:
        return 1.0
    ctx = set(tokenize(context))
    ok = sum(1 for s in sents if len(set(tokenize(s)) & ctx) / len(set(tokenize(s))) >= 0.6)
    return ok / len(sents)


def llm_faithfulness(rag: RAG, answer: str, context: str) -> float | None:
    prompt = (f"CONTEXT:\n{context[:6000]}\n\nANSWER:\n{answer}\n\n"
              "Split the ANSWER into factual claims. For each, is it fully supported by the CONTEXT? "
              'Reply JSON only: {"claims": [{"claim": "...", "supported": true}]}')
    try:
        r = rag.llm.complete("You are a strict fact-checking judge. JSON only.",
                             [{"role": "user", "content": prompt}], model=rag.s.fast_model(),
                             max_tokens=600, temperature=0, json_mode=True)
        claims = parse_json(r.text).get("claims", [])
        return sum(bool(c.get("supported")) for c in claims) / len(claims) if claims else 1.0
    except Exception as e:
        print("  [judge] failed:", e)
        return None


def answer_metrics(rag: RAG, tests: list[dict]) -> tuple[dict, list[dict]]:
    rows = []
    for i, t in enumerate(tests):
        if i and PACE:
            time.sleep(PACE)
        t0 = time.time()
        a = rag.ask(t["q"], history=t.get("history", []))
        latency = time.time() - t0
        ans_n = normalize(a.answer)
        row = {"id": t["id"], "type": t["type"], "q": t["q"], "answer": a.answer[:400],
               "refused": a.refused, "latency": round(latency, 2), "cost": a.cost_usd,
               "cited": [c["source"] for c in a.citations], "confidence": a.confidence}
        if t.get("refuse"):
            row["correct"] = a.refused
            row["refusal_ok"] = a.refused
        else:
            row["refusal_ok"] = not a.refused
            row["correct"] = (not a.refused) and all(normalize(m) in ans_n for m in t.get("must", []))
            row["citation_ok"] = ("*" in t["gold_sources"] and bool(row["cited"])) or \
                any(s in t["gold_sources"] for s in row["cited"])
            context = "\n".join(c["snippet"] for c in a.retrieved)
            f = llm_faithfulness(rag, a.body or a.answer, context) if (rag.llm.available and not NO_JUDGE) else None
            row["faithfulness"] = round(f if f is not None else lexical_faithfulness(a.body or a.answer, context), 3)
            row["judge"] = "llm" if f is not None else "lexical"
        rows.append(row)
        print(f"  {'PASS' if row['correct'] else 'FAIL'}  {t['id']} [{t['type']}] {t['q'][:60]}")
    ins = [r for r in rows if "citation_ok" in r]
    oos = [r for r in rows if r["type"] == "out_of_scope"]
    lat = sorted(r["latency"] for r in rows)
    summary = {
        "answer_accuracy": round(sum(r["correct"] for r in rows) / len(rows), 3),
        "in_scope_accuracy": round(sum(r["correct"] for r in ins) / (len(ins) or 1), 3),
        "refusal_accuracy_oos": round(sum(r["refused"] for r in oos) / (len(oos) or 1), 3),
        "false_refusals": sum(r["refused"] for r in ins),
        "citation_accuracy": round(sum(r["citation_ok"] for r in ins) / (len(ins) or 1), 3),
        "faithfulness": (round(statistics.mean(r["faithfulness"] for r in ins if not r["refused"]), 3)
                         if any(not r["refused"] for r in ins) else None),
        "latency_avg_s": round(statistics.mean(lat), 2),
        "latency_p95_s": lat[min(len(lat) - 1, int(0.95 * len(lat)))],
        "cost_per_answer_usd": round(statistics.mean(r["cost"] for r in rows), 5),
    }
    return summary, rows


def write_report(cfg: dict, retrieval: list[dict], summary: dict | None, rows: list[dict]) -> Path:
    L = ["# Evaluation report", "",
         f"- Date: {time.strftime('%Y-%m-%d %H:%M')}",
         f"- Embedder: `{cfg['embedder']}` · LLM: `{cfg['llm']}` · mode: `{cfg['mode']}` · "
         f"k={cfg['k']} · chunk={cfg['chunk']}", f"- Test questions: {cfg['n']} "
         f"({cfg['types']})", "", "## Retrieval", "",
         "| Mode | k | Hit@k (Recall) | Precision@k | MRR | Missed |", "|---|---|---|---|---|---|"]
    for r in retrieval:
        L.append(f"| {r['mode']} | {r['k']} | {r['hit@k']:.0%} | {r['precision@k']:.0%} | "
                 f"{r['mrr']:.2f} | {', '.join(r['misses']) or '-'} |")
    if summary:
        L += ["", "## Answers", "", "| Metric | Value |", "|---|---|"]
        for k, v in summary.items():
            L.append(f"| {k} | {v:.0%} |" if isinstance(v, float) and v <= 1 and "latency" not in k
                     and "cost" not in k else f"| {k} | {v} |")
        L += ["", "## Per question", "", "| id | type | result | refused | cited | faithfulness | s |",
              "|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append(f"| {r['id']} | {r['type']} | {'✅' if r['correct'] else '❌'} | {r['refused']} | "
                     f"{', '.join(sorted(set(r['cited']))) or '-'} | {r.get('faithfulness', '-')} | {r['latency']} |")
        fails = [r for r in rows if not r["correct"]]
        L += ["", "## Error analysis (fill the 'why' + 'fix' columns)", ""]
        if fails:
            L += ["| id | question | answer (start) | why it failed | fix tried |", "|---|---|---|---|---|"]
            for r in fails:
                L.append(f"| {r['id']} | {r['q']} | {r['answer'][:90].replace(chr(10), ' ')} | | |")
        else:
            L.append("All test questions passed.")
    out = HERE / "report.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset", default=str(HERE / ("testset_paluniv.json" if (HERE / "testset_paluniv.json").exists() else "testset.json")))
    ap.add_argument("--compare", action="store_true", help="compare retrieval modes and k")
    ap.add_argument("--retrieval-only", action="store_true")
    ap.add_argument("--pace", type=float, default=4, help="seconds between questions (free-tier rate limits)")
    ap.add_argument("--no-judge", action="store_true", help="lexical faithfulness only (saves free-tier quota)")
    args = ap.parse_args()
    global NO_JUDGE, PACE
    NO_JUDGE, PACE = args.no_judge, args.pace
    tests = json.loads(Path(args.testset).read_text(encoding="utf-8"))
    rag = RAG()
    print(f"Index: {rag.index.info.get('chunks')} chunks · embedder {rag.index.info.get('embedder')}")
    retrieval = []
    if args.compare:
        for mode in ("bm25", "dense", "hybrid"):
            for k in (1, 3, 5):
                retrieval.append(retrieval_metrics(rag, tests, k, mode))
    else:
        retrieval.append(retrieval_metrics(rag, tests, rag.s.top_k, rag.s.retrieval_mode))
    for r in retrieval:
        print(f"  retrieval {r['mode']:6s} k={r['k']}: hit {r['hit@k']:.0%}  "
              f"P@k {r['precision@k']:.0%}  MRR {r['mrr']:.2f}  misses {r['misses']}")
    summary, rows = (None, [])
    if not args.retrieval_only:
        summary, rows = answer_metrics(rag, tests)
        print(json.dumps(summary, indent=1))
    cfg = {"embedder": rag.index.info.get("embedder"), "llm": f"{rag.s.llm_provider}:{rag.s.default_model()}",
           "mode": rag.s.retrieval_mode, "k": rag.s.top_k, "chunk": f"{rag.s.chunk_size}/{rag.s.chunk_overlap}",
           "n": len(tests), "types": ", ".join(sorted({t['type'] for t in tests}))}
    out = write_report(cfg, retrieval, summary, rows)
    (HERE / "results.json").write_text(json.dumps({"config": cfg, "retrieval": retrieval,
                                                   "summary": summary, "rows": rows},
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    hist = HERE / "history.jsonl"                    # log every run -> before/after evidence
    with hist.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"time": time.strftime("%H:%M"), **cfg, "retrieval": retrieval[-1],
                            "summary": summary}, ensure_ascii=False) + "\n")
    print(f"\nReport -> {out}")


if __name__ == "__main__":
    main()
