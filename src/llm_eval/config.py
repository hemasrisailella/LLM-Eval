from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

STUDY_IDS = ("sycophancy", "prompt_sensitivity")


def find_project_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "config.yaml").is_file() and (candidate / "studies").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not find project root (config.yaml + studies/). "
        "Run commands from the open-llm-eval directory."
    )


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(study_id: str, root: Path | None = None) -> dict[str, Any]:
    if study_id not in STUDY_IDS:
        raise ValueError(f"Unknown study '{study_id}'. Choose from: {', '.join(STUDY_IDS)}")

    root = (root or find_project_root()).resolve()
    study_path = root / "studies" / study_id / "config.yaml"
    if not study_path.is_file():
        raise FileNotFoundError(f"Missing study config: {study_path}")

    with (root / "config.yaml").open(encoding="utf-8") as f:
        base = yaml.safe_load(f) or {}
    with study_path.open(encoding="utf-8") as f:
        study = yaml.safe_load(f) or {}

    cfg = _deep_merge(base, study)
    cfg["study_id"] = study_id
    cfg["root"] = root

    paths = cfg.get("paths", {})
    cfg["paths"] = {key: (root / rel).resolve() for key, rel in paths.items()}

    templates_rel = cfg.get("prompts", {}).get("templates")
    if templates_rel:
        cfg["prompts"]["templates_path"] = (root / templates_rel).resolve()

    styles_rel = cfg.get("prompts", {}).get("styles")
    if styles_rel:
        cfg["prompts"]["styles_path"] = (root / styles_rel).resolve()

    return cfg
