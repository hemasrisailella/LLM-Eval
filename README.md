# LLM-Eval: Open LLM Reliability Evaluation Framework

Benchmarks report one number: accuracy averaged over a static test set. That
number is silent about the failures users actually meet, a model that abandons
a correct answer because the user asserts a wrong one, or a model whose answer
changes when the same question is wrapped in a different instruction.

This repository is a small framework for measuring those failures, plus two
studies run through it on **Qwen2.5-7B-Instruct** and **Llama-3.1-8B-Instruct**.



## Studies

| Study | Question | Design | Scoring |
|-------|----------|--------|---------|
| **sycophancy** | Does a user's stated wrong answer move the model off a correct one? | 100 MCQ items × 5 pressure conditions | automatic (option letter) |
| **prompt_sensitivity** | How stable are answers and explanations under meaning-preserving paraphrase? | 30 problems × 8 instruction wrappers | automatic (`FINAL ANSWER:`) |

See `studies/registry.yaml` for the canonical list.

## Headline findings

- **Both models are sycophantic**. Llama's
  wrong-agreement rises 0.11 → 0.18 and Qwen's 0.02 → 0.09 under pressure.
- **Rhetorical intensity doesn't matter**. The step
  that costs you is "no user claim" → "some user claim"; escalating to
  *"Don't disagree with me"* actually produces the *lowest* wrong-agreement.
- **Prompt style doesn't move the average but moves the answers**: 61.4% (Llama) and 30.0% (Qwen) of items change answer
  relative to the neutral wrapper. The same accuracy is assembled from a
  different set of correct items each time.
- **Fragility is a cheap, label-free robustness signal** — it correlates with
  accuracy at *r* = 0.81 and separated the two models where aggregate accuracy
  could not.

## Layout

```
llm-eval/
├── config.yaml                   # shared models + inference (device, dtype, decoding)
├── studies/
│   ├── registry.yaml             # canonical study list
│   ├── sycophancy/
│   │   ├── config.yaml           # models, active prompts, paths
│   │   ├── data/questions.jsonl  # 100 MCQ items with a designated wrong option
│   │   ├── prompts/templates.yaml
│   │   ├── results/{raw,metrics}/
│   │   └── analysis/figures/
│   └── prompt_sensitivity/
│       └── ...                   # + prompts/styles.yaml (the 8 wrappers)
├── src/llm_eval/                 # shared library
│   ├── config.py                 # layered config loading, STUDY_IDS
│   ├── inference.py              # generation loop + response records
│   ├── io_utils.py               # JSONL I/O, collect_raw_responses
│   ├── prompts.py
│   └── studies/<id>/             # dataset, parsing, metrics, plots per study
├── scripts/                      # CLI — every entry point takes --study
├── slurm/                        # single-GPU job template
```

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# --- Sycophancy ---
python scripts/build_dataset.py    --study sycophancy
python scripts/run_evaluation.py   --study sycophancy --limit 5   # drop --limit for the full run
python scripts/compute_metrics.py  --study sycophancy
python scripts/plot_results.py     --study sycophancy

# --- Prompt sensitivity ---
python scripts/build_dataset.py    --study prompt_sensitivity
python scripts/run_evaluation.py   --study prompt_sensitivity --limit 5
python scripts/compute_metrics.py  --study prompt_sensitivity
python scripts/plot_results.py     --study prompt_sensitivity
```

## Metrics

**Sycophancy**

- **Wrong-agreement rate** — fraction of responses matching the user-suggested
  wrong answer.
- **Flip rate** — among items correct under `C0` (neutral), how often the model
  picks the user's wrong option under `C1`–`C4`. The `C0` row is the base rate
  for that distractor with no user present, so the quantity to interpret is the
  **increment** over it, not the level.

**Prompt sensitivity**

- **Answer consistency** — per problem, the fraction of wrappers sharing the
  most common parsed answer. **Fragility** is `1 − consistency`.
- **Churn** — fraction of (problem, wrapper) pairs whose answer differs from the
  neutral wrapper's.
- **Explanation similarity** — mean pairwise Jaccard over the text before
  `FINAL ANSWER:`.
- **Sensitivity map** — per-item correct/wrong across wrappers.

Consistency is deliberately agnostic to correctness: a model that returns the
same wrong answer under all eight wrappers is perfectly consistent and perfectly
wrong. That separation is the point.
