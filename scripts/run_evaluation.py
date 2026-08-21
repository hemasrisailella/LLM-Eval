#!/usr/bin/env python3
"""Run behavioral evaluation for a study across models and prompt conditions."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import ROOT, add_study_arg, bootstrap_imports

bootstrap_imports()

from llm_eval.config import load_config
from llm_eval.inference import run_behavioral_evaluation


def main() -> None:
    parser = argparse.ArgumentParser()
    add_study_arg(parser)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--limit", type=int, default=None, help="Debug: cap questions")
    parser.add_argument("--models", nargs="*", help="Subset of model names from config")
    parser.add_argument("--prompts", nargs="*", help="Subset of prompt ids")
    args = parser.parse_args()

    cfg = load_config(args.study, args.root)

    models = cfg["models"]["behavioral"]
    if args.models:
        models = [m for m in models if m["name"] in args.models]

    prompt_ids = args.prompts or cfg["prompts"]["active"]
    inf = cfg["inference"]
    passthrough = cfg.get("response_fields", [])

    run_behavioral_evaluation(
        study_id=args.study,
        questions_path=Path(cfg["paths"]["questions"]),
        templates_path=Path(cfg["prompts"]["templates_path"]),
        output_dir=Path(cfg["paths"]["raw_responses"]),
        models=models,
        prompt_ids=prompt_ids,
        device=inf["device"],
        dtype=inf["dtype"],
        temperature=inf["temperature"],
        do_sample=inf["do_sample"],
        limit=args.limit,
        extra_response_fields=passthrough,
    )


if __name__ == "__main__":
    main()
