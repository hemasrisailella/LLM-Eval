# Prompt sensitivity dataset schema

## `problems.jsonl` (base problems)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | e.g. `arith_001` |
| `base_question` | string | Core reasoning question |
| `gold_answer` | string | Reference final answer |
| `category` | string | arithmetic, logic, commonsense, symbolic, trick |
| `difficulty` | string | easy / medium / hard |
| `answer_type` | string | integer, number, text, yes_no |

## `questions.jsonl` (expanded eval items)

One row per `(problem, prompt_style)` — 30 problems × 8 styles = 240 items by default.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | e.g. `arith_001__step_by_step` |
| `problem_id` | string | Links to base problem |
| `prompt_style` | string | neutral, step_by_step, … |
| `question` | string | Full wrapped prompt (passed to model) |
| `gold_answer` | string | Same as base problem |

Paraphrase wrappers live in `prompts/styles.yaml`.
