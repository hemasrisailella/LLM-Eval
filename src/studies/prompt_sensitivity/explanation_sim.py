from __future__ import annotations

import re
from itertools import combinations

import pandas as pd

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def token_set(text: str) -> set[str]:
    return set(_TOKEN_RE.findall((text or "").lower()))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def mean_pairwise_explanation_similarity(texts: list[str]) -> float:
    if len(texts) < 2:
        return 1.0
    sets = [token_set(t) for t in texts]
    scores = [jaccard(a, b) for a, b in combinations(sets, 2)]
    return float(sum(scores) / len(scores)) if scores else 1.0


def explanation_similarity_by_problem(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["model", "problem_id"]
    for keys, sub in scored.groupby(group_cols):
        model, problem_id = keys
        sim = mean_pairwise_explanation_similarity(sub["explanation_text"].tolist())
        rows.append(
            {
                "model": model,
                "problem_id": problem_id,
                "explanation_similarity": sim,
                "category": sub["category"].iloc[0],
            }
        )
    return pd.DataFrame(rows)
