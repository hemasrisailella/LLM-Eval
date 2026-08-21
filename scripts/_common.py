from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def add_study_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--study",
        required=True,
        choices=["unanswerable", "sycophancy", "prompt_sensitivity"],
        help="Which evaluation study to run",
    )


def bootstrap_imports() -> None:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
