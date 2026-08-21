from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def collect_raw_responses(raw_dir: str | Path) -> "pd.DataFrame":
    """Load every ``*.jsonl`` response file in ``raw_dir`` into one DataFrame.

    Shared by all study scorers: raw generations are written one file per
    (model, prompt condition), and every metric module starts by concatenating
    them.
    """
    import pandas as pd

    frames: list[pd.DataFrame] = []
    for path in sorted(Path(raw_dir).glob("*.jsonl")):
        frames.append(pd.DataFrame(read_jsonl(path)))
    if not frames:
        raise FileNotFoundError(f"No .jsonl files in {raw_dir}")
    return pd.concat(frames, ignore_index=True)
