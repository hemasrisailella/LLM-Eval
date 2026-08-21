from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_prompt_templates(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_prompt(template: str, record: dict[str, Any] | str) -> str:
    """Format a prompt template using fields from a question record."""
    if isinstance(record, str):
        return template.format(question=record).strip()

    ctx = dict(record)
    if "text" in ctx and "question" not in ctx:
        ctx["question"] = ctx["text"]
    return template.format(**ctx).strip()
