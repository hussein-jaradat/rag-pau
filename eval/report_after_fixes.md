# Evaluation report

- Date: 2026-11-07 12:54
- Embedder: `local:intfloat/multilingual-e5-small` · LLM: `gemini:gemini-3.8-flash` · mode: `hybrid` · k=5 · chunk=900/150
- Test questions: 15 (dialect, direct, followup, multi_hop, not_in_docs, out_of_scope, table)

## Retrieval

| Mode | k | Hit@k (Recall) | Precision@k | MRR | Missed |
|---|---|---|---|---|---|
| hybrid | 5 | 83% | 42% | 0.66 | p07, p08 |

## Answers

| Metric | Value |
|---|---|
| answer_accuracy | 60% |
| in_scope_accuracy | 75% |
| refusal_accuracy_oos | 0% |
| false_refusals | 0 |
| citation_accuracy | 100% |
| faithfulness | 97% |
| latency_avg_s | 0.52 |
| latency_p95_s | 0.87 |
| cost_per_answer_usd | 0.0 |

## Per question

| id | type | result | refused | cited | faithfulness | s |
|---|---|---|---|---|---|---|
| p01 | direct | ✅ | False | admission_registration_regulations.html | 1.0 | 0.49 |
| p02 | dialect | ❌ | False | admission_registration_regulations.html | 1.0 | 0.47 |
| p03 | direct | ✅ | False | admission_registration_regulations.html | 0.667 | 0.47 |
| p04 | direct | ✅ | False | programs/139134.html, programs/3200.html | 1.0 | 0.45 |
| p05 | table | ✅ | False | programs/139833.html, programs/144596.html, programs/16232.html | 1.0 | 0.44 |
| p06 | direct | ❌ | False | programs/3207.html | 1.0 | 0.87 |
| p07 | dialect | ❌ | False | programs/3207.html, programs/4446.html | 1.0 | 0.41 |
| p08 | direct | ✅ | False | admission_registration_regulations.html, bachelor_requirements.html, student_guide_2024_2025.pdf | 1.0 | 0.47 |
| p09 | dialect | ✅ | False | admission_registration_regulations.html | 1.0 | 0.47 |
| p10 | direct | ✅ | False | admission_registration_regulations.html | 1.0 | 0.56 |
| p11 | multi_hop | ✅ | False | admission_registration_regulations.html, programs/4446.html | 1.0 | 0.57 |
| p12 | followup | ✅ | False | programs/139134.html, programs/3200.html | 1.0 | 0.61 |
| p13 | not_in_docs | ❌ | False | admission_registration_regulations.html | - | 0.5 |
| p14 | out_of_scope | ❌ | False | admission_faq.html, student_guide_2024_2025.pdf | - | 0.56 |
| p15 | out_of_scope | ❌ | False | new_students_enrollment.html | - | 0.51 |

## Error analysis (fill the 'why' + 'fix' columns)

| id | question | answer (start) | why it failed | fix tried |
|---|---|---|---|---|
| p02 | كم ساعة بقدر أسجل بالفصل كحد أقصى؟ | أقرب ما وجدته في المستندات: • ب-أن يكون تخرج الطالب متوقفاً على السماح له بدراسة (21) ساعة | | |
| p06 | كم عدد الساعات المعتمدة لبرنامج تكنولوجيا المعلومات؟ | أقرب ما وجدته في المستندات: • برنامج تكنولوجيا المعلومات - جامعة فلسطين الأهلية | الخطة ال | | |
| p07 | شو لازم أجيب بمواد البرمجة الأولى عشان أكمل بتخصص تكنولوجيا المعلومات؟ | أقرب ما وجدته في المستندات: • برنامج تكنولوجيا المعلومات - جامعة فلسطين الأهلية | الخطة ال | | |
| p13 | متى موعد امتحان الخوارزميات الأسبوع القادم؟ | أقرب ما وجدته في المستندات: • الامتحان النهائي: · إذا تغيب الطالب عن الامتحان النهائي بدون | | |
| p14 | اكتب لي قصيدة عن الجامعة | أقرب ما وجدته في المستندات: • | https://palunليiv.eدdعuل.اp دsع/?اسpaلمgeا_id=140276 | [1] | | |
| p15 | من فاز بكأس العالم 2022؟ | أقرب ما وجدته في المستندات: • | كلية العلوم الإنسانية والتربوية | برنامج رياض الأطفال | يق | | |