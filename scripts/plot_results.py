#!/usr/bin/env python3
"""Generate figures for a study."""

from __future__ import annotations

import argparse
from pathlib import Path

import seaborn as sns

from _common import ROOT, add_study_arg, bootstrap_imports

bootstrap_imports()

from llm_eval.config import load_config


def _plot_prompt_sensitivity(cfg: dict) -> None:
    from llm_eval.studies.prompt_sensitivity.plots import (
        plot_accuracy_by_style,
        plot_explanation_vs_consistency,
        plot_fragility_by_category,
        plot_fragility_histogram,
        plot_sensitivity_heatmap,
    )

    fig_dir = Path(cfg["paths"]["figures"])
    fig_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = Path(cfg["paths"]["metrics"])
    style_order = cfg["prompts"].get("style_order")

    plot_accuracy_by_style(
        metrics_dir / "accuracy_by_style.csv",
        fig_dir / "accuracy_by_style.png",
        style_order=style_order,
    )
    plot_fragility_by_category(
        metrics_dir / "fragility_by_category.csv",
        fig_dir / "fragility_by_category.png",
    )
    plot_fragility_histogram(
        metrics_dir / "problem_stability.csv",
        fig_dir / "fragility_histogram.png",
    )
    plot_sensitivity_heatmap(
        metrics_dir / "sensitivity_map.csv",
        fig_dir / "sensitivity_map.png",
        style_order=style_order,
    )
    plot_explanation_vs_consistency(
        metrics_dir / "problem_stability_with_explanations.csv",
        fig_dir / "explanation_vs_consistency.png",
    )


def _plot_sycophancy(cfg: dict) -> None:
    from llm_eval.studies.sycophancy.plots import (
        plot_flip_rates_by_condition,
        plot_wrong_agreement_by_model,
    )

    fig_dir = Path(cfg["paths"]["figures"])
    fig_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = Path(cfg["paths"]["metrics"])
    flip_csv = metrics_dir / "flip_rates.csv"
    plot_flip_rates_by_condition(flip_csv, fig_dir / "flip_rate_by_condition.png")
    plot_wrong_agreement_by_model(flip_csv, fig_dir / "wrong_agreement_by_model.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    add_study_arg(parser)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    cfg = load_config(args.study, args.root)
    sns.set_theme(style="whitegrid")

    if args.study == "sycophancy":
        _plot_sycophancy(cfg)
    elif args.study == "prompt_sensitivity":
        _plot_prompt_sensitivity(cfg)

    print(f"Figures saved under {cfg['paths']['figures']}")


if __name__ == "__main__":
    main()
