# Evaluation report

- Date: 2026-11-07 13:29
- Embedder: `local:intfloat/multilingual-e5-small` · LLM: `groq:qwen/qwen3.8-27b` · mode: `hybrid` · k=4 · chunk=900/150
- Test questions: 15 (dialect, direct, followup, multi_hop, not_in_docs, out_of_scope, table)

## Retrieval

| Mode | k | Hit@k (Recall) | Precision@k | MRR | Missed |
|---|---|---|---|---|---|
| hybrid | 4 | 92% | 48% | 0.81 | p08 |

## Answers

| Metric | Value |
|---|---|
| answer_accuracy | 87% |
| in_scope_accuracy | 83% |
| refusal_accuracy_oos | 100% |
| false_refusals | 2 |
| citation_accuracy | 83% |
| faithfulness | 84% |
| latency_avg_s | 3.08 |
| latency_p95_s | 8.71 |
| cost_per_answer_usd | 0.00493 |

## Per question

| id | type | result | refused | cited | faithfulness | s |
|---|---|---|---|---|---|---|
| p01 | direct | ✅ | False | admission_registration_regulations.html | 0.8 | 1.29 |
| p02 | dialect | ✅ | False | admission_registration_regulations.html | 0.8 | 5.68 |
| p03 | direct | ✅ | False | bachelor_requirements.html | 1.0 | 8.71 |
| p04 | direct | ✅ | False | programs/3200.html | 1.0 | 4.28 |
| p05 | table | ❌ | True | - | 0.0 | 0.94 |
| p06 | direct | ✅ | False | programs/3207.html | 1.0 | 0.95 |
| p07 | dialect | ✅ | False | programs/3207.html | 1.0 | 1.25 |
| p08 | direct | ❌ | True | - | 0.0 | 0.91 |
| p09 | dialect | ✅ | False | admission_registration_regulations.html | 1.0 | 1.41 |
| p10 | direct | ✅ | False | admission_registration_regulations.html | 0.75 | 4.5 |
| p11 | multi_hop | ✅ | False | admission_registration_regulations.html | 0.0 | 1.51 |
| p12 | followup | ✅ | False | admission_faq.html, bachelor_requirements.html | 1.0 | 6.23 |
| p13 | not_in_docs | ✅ | True | - | - | 0.9 |
| p14 | out_of_scope | ✅ | True | - | - | 1.5 |
| p15 | out_of_scope | ✅ | True | - | - | 6.16 |

## Error analysis (fill the 'why' + 'fix' columns)

| id | question | answer (start) | why it failed | fix tried |
|---|---|---|---|---|
| p05 | كم ساعة معتمدة لمساق أساسيات الحاسوب والبرمجة؟ | عذراً، لا تتوفر لدي معلومات عن هذا السؤال في المستندات المتاحة. يرجى مراجعة عمادة القبول و | | |
| p08 | ما هي أقصى مدة لإنهاء درجة البكالوريوس؟ | عذراً، لا تتوفر لدي معلومات عن هذا السؤال في المستندات المتاحة. يرجى مراجعة عمادة القبول و | | |