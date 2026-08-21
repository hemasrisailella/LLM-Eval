#!/usr/bin/env python3
"""Compute study metrics from stored raw responses."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import ROOT, add_study_arg, bootstrap_imports

bootstrap_imports()

from llm_eval.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    add_study_arg(parser)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    cfg = load_config(args.study, args.root)

    if args.study == "sycophancy":
        from llm_eval.studies.sycophancy.metrics import (
            save_metrics_report,
            score_raw_responses,
        )

        scored = score_raw_responses(Path(cfg["paths"]["raw_responses"]))
        neutral_id = cfg["prompts"].get("neutral_id", "C0")
        save_metrics_report(
            scored,
            Path(cfg["paths"]["metrics"]),
            neutral_id=neutral_id,
        )
    elif args.study == "prompt_sensitivity":
        from llm_eval.studies.prompt_sensitivity.metrics import (
            save_metrics_report,
            score_raw_responses,
        )

        scored = score_raw_responses(Path(cfg["paths"]["raw_responses"]))
        save_metrics_report(
            scored,
            Path(cfg["paths"]["metrics"]),
            baseline_style=cfg["prompts"].get("baseline_style", "neutral"),
        )
    else:
        raise ValueError(f"Unhandled study: {args.study}")

    print(f"Metrics written to {cfg['paths']['metrics']}")


if __name__ == "__main__":
    main()
