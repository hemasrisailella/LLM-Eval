from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

from llm_eval.studies.prompt_sensitivity.explanation_sim import (
    explanation_similarity_by_problem,
)
from llm_eval.studies.prompt_sensitivity.parsing import score_row
from llm_eval.io_utils import collect_raw_responses


def _safe_rate(num: float, den: float) -> float:
    return float(num / den) if den else 0.0


def score_raw_responses(raw_dir: Path) -> pd.DataFrame:
    df = collect_raw_responses(raw_dir)
    scored = df.apply(lambda r: pd.Series(score_row(r)), axis=1)
    return pd.concat([df, scored], axis=1)


def answer_consistency(sub: pd.DataFrame) -> float:
    answers = sub["parsed_normalized"].tolist()
    # Ignore empty parses for consistency denominator
    valid = [a for a in answers if a]
    if not valid:
        return 0.0
    counts = Counter(valid)
    return counts.most_common(1)[0][1] / len(valid)


def compute_problem_stability(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, problem_id), sub in scored.groupby(["model", "problem_id"]):
        cons = answer_consistency(sub)
        rows.append(
            {
                "model": model,
                "problem_id": problem_id,
                "category": sub["category"].iloc[0],
                "difficulty": sub["difficulty"].iloc[0],
                "n_styles": len(sub),
                "answer_consistency": cons,
                "fragility": 1.0 - cons,
                "accuracy_mean": sub["is_correct"].mean(),
                "n_unique_answers": sub["parsed_normalized"].nunique(),
            }
        )
    return pd.DataFrame(rows)


def accuracy_by_style(scored: pd.DataFrame) -> pd.DataFrame:
    return (
        scored.groupby(["model", "prompt_style"])
        .agg(
            accuracy=("is_correct", "mean"),
            n=("is_correct", "count"),
        )
        .reset_index()
        .sort_values(["model", "accuracy"], ascending=[True, False])
    )


def accuracy_by_category(scored: pd.DataFrame) -> pd.DataFrame:
    return (
        scored.groupby(["model", "category", "prompt_style"])
        .agg(accuracy=("is_correct", "mean"), n=("is_correct", "count"))
        .reset_index()
    )


def build_sensitivity_map(scored: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows=problem_id, columns=prompt_style, values=is_correct (mean if multi-run)."""
    pivot = scored.pivot_table(
        index=["model", "problem_id", "category"],
        columns="prompt_style",
        values="is_correct",
        aggfunc="mean",
    )
    return pivot.reset_index()


def save_metrics_report(
    scored: pd.DataFrame,
    output_dir: Path,
    baseline_style: str = "neutral",
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    stability = compute_problem_stability(scored)
    expl_sim = explanation_similarity_by_problem(scored)[
        ["model", "problem_id", "explanation_similarity"]
    ]
    merged_stability = stability.merge(expl_sim, on=["model", "problem_id"], how="left")

    by_style = accuracy_by_style(scored)
    by_category = accuracy_by_category(scored)
    sensitivity = build_sensitivity_map(scored)

    stability.to_csv(output_dir / "problem_stability.csv", index=False)
    merged_stability.to_csv(output_dir / "problem_stability_with_explanations.csv", index=False)
    by_style.to_csv(output_dir / "accuracy_by_style.csv", index=False)
    by_category.to_csv(output_dir / "accuracy_by_category.csv", index=False)
    sensitivity.to_csv(output_dir / "sensitivity_map.csv", index=False)

    # Category-level mean fragility
    cat_frag = (
        merged_stability.groupby(["model", "category"])
        .agg(
            mean_fragility=("fragility", "mean"),
            mean_consistency=("answer_consistency", "mean"),
            mean_explanation_sim=("explanation_similarity", "mean"),
        )
        .reset_index()
    )
    cat_frag.to_csv(output_dir / "fragility_by_category.csv", index=False)

    summary = {
        "baseline_style": baseline_style,
        "n_responses": int(len(scored)),
        "n_problems": int(scored["problem_id"].nunique()),
        "overall_accuracy": _safe_rate(scored["is_correct"].sum(), len(scored)),
        "mean_answer_consistency": float(stability["answer_consistency"].mean()),
        "mean_fragility": float(stability["fragility"].mean()),
        "mean_explanation_similarity": float(expl_sim["explanation_similarity"].mean()),
        "best_style": by_style.groupby("model")["accuracy"].idxmax().to_dict()
        if len(by_style)
        else {},
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    # Answer changed vs baseline (neutral) per problem
    change_rows = []
    for (model, problem_id), sub in scored.groupby(["model", "problem_id"]):
        base = sub[sub["prompt_style"] == baseline_style]
        if base.empty:
            continue
        base_ans = base["parsed_normalized"].iloc[0]
        for _, row in sub.iterrows():
            if row["prompt_style"] == baseline_style:
                continue
            change_rows.append(
                {
                    "model": model,
                    "problem_id": problem_id,
                    "prompt_style": row["prompt_style"],
                    "answer_changed_from_baseline": row["parsed_normalized"] != base_ans,
                    "category": row["category"],
                }
            )
    if change_rows:
        pd.DataFrame(change_rows).to_csv(
            output_dir / "answer_changes_from_baseline.csv", index=False
        )
