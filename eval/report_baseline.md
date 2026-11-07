# Evaluation report

- Date: 2026-11-07 12:05
- Embedder: `tfidf:char2-5` · LLM: `offline:qwen/qwen3.8-27b` · mode: `hybrid` · k=4 · chunk=900/150
- Test questions: 16 (conflict, cross_lingual, dialect, direct, followup, multi_hop, out_of_scope, reworded)

## Retrieval

| Mode | k | Hit@k (Recall) | Precision@k | MRR | Missed |
|---|---|---|---|---|---|
| hybrid | 4 | 92% | 23% | 0.92 | q06 |

## Answers

| Metric | Value |
|---|---|
| answer_accuracy | 94% |
| in_scope_accuracy | 92% |
| refusal_accuracy_oos | 100% |
| false_refusals | 0 |
| citation_accuracy | 92% |
| faithfulness | 100% |
| latency_avg_s | 0.0 |
| latency_p95_s | 0.0 |
| cost_per_answer_usd | 0.0 |

## Per question

| id | type | result | refused | cited | faithfulness | s |
|---|---|---|---|---|---|---|
| q01 | direct | ✅ | False | student_regulations_2024.md | 1.0 | 0.0 |
| q02 | dialect | ✅ | False | student_regulations_2024.md | 1.0 | 0.0 |
| q03 | direct | ✅ | False | cs_courses.csv | 1.0 | 0.0 |
| q04 | reworded | ✅ | False | cs_courses.csv | 1.0 | 0.0 |
| q05 | direct | ✅ | False | registration_guide_en.pdf | 1.0 | 0.0 |
| q06 | cross_lingual | ❌ | False | cs_courses.csv, student_regulations_2024.md | 1.0 | 0.0 |
| q07 | dialect | ✅ | False | cs_courses.csv, student_regulations_2024.md | 1.0 | 0.0 |
| q08 | conflict | ✅ | False | student_regulations_2024.md | 1.0 | 0.0 |
| q09 | direct | ✅ | False | cs_courses.csv, student_regulations_2024.md | 1.0 | 0.0 |
| q10 | reworded | ✅ | False | registration_guide_en.pdf | 1.0 | 0.0 |
| q11 | multi_hop | ✅ | False | student_regulations_2024.md | 1.0 | 0.0 |
| q12 | direct | ✅ | False | registration_guide_en.pdf | 1.0 | 0.0 |
| q13 | out_of_scope | ✅ | True | - | - | 0.0 |
| q14 | out_of_scope | ✅ | True | - | - | 0.0 |
| q15 | out_of_scope | ✅ | True | - | - | 0.0 |
| q16 | followup | ✅ | False | student_regulations_2024.md | 1.0 | 0.0 |

## Error analysis (fill the 'why' + 'fix' columns)

| id | question | answer (start) | why it failed | fix tried |
|---|---|---|---|---|
| q06 | كم سعر الساعة المعتمدة؟ | أقرب ما وجدته في المستندات: • رقم المساق: CS499; اسم المساق: مشروع التخرج; الساعات: 4; الم | | |