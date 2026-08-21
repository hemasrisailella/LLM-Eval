#!/usr/bin/env python3
"""Build questions.jsonl for a registered study."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import ROOT, add_study_arg, bootstrap_imports

bootstrap_imports()

from llm_eval.config import load_config
from llm_eval.io_utils import write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    add_study_arg(parser)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    cfg = load_config(args.study, args.root)

    if args.study == "sycophancy":
        from llm_eval.studies.sycophancy.dataset import build_question_records

        records = build_question_records(target_size=cfg["dataset"]["target_size"])
        out = Path(cfg["paths"]["questions"])
        write_jsonl(out, records)
        print(f"Wrote {len(records)} questions to {out}")

    elif args.study == "prompt_sensitivity":
        from llm_eval.studies.prompt_sensitivity.dataset import build_datasets

        ds = cfg["dataset"]
        problems, questions = build_datasets(
            styles_path=Path(cfg["prompts"]["styles_path"]),
            style_order=cfg["prompts"]["style_order"],
            categories=ds.get("categories"),
            per_category=ds.get("problems_per_category", 6),
        )
        write_jsonl(Path(cfg["paths"]["problems"]), problems)
        write_jsonl(Path(cfg["paths"]["questions"]), questions)
        print(f"Wrote {len(problems)} problems to {cfg['paths']['problems']}")
        print(f"Wrote {len(questions)} prompt items to {cfg['paths']['questions']}")

    else:
        raise ValueError(f"Unhandled study: {args.study}")


if __name__ == "__main__":
    main()
