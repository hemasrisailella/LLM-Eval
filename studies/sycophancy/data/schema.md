# Sycophancy dataset schema (`questions.jsonl`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | e.g. `syc_0001` |
| `question` | string | Factual question |
| `correct_answer` | string | Gold answer text |
| `wrong_answer` | string | Plausible user-suggested wrong answer |
| `category` | string | geography, math, misconception, … |
| `option_a` … `option_d` | string | Shuffled MCQ options |
| `correct_choice` | string | Letter A–D for correct option |
| `wrong_choice` | string | Letter A–D for user-wrong option |

Prompt conditions `C0`–`C4` are defined in `prompts/templates.yaml`.
