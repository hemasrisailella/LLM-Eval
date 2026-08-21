from __future__ import annotations

import re
from typing import Any

_FINAL_ANSWER_RE = re.compile(
    r"FINAL\s+ANSWER\s*:\s*(.+?)(?:\n|$)",
    re.IGNORECASE | re.DOTALL,
)
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def normalize_answer(text: str | None, answer_type: str = "text") -> str:
    if text is None:
        return ""
    s = str(text).strip().lower()
    s = s.rstrip(".")
    s = s.replace(",", "")
    if answer_type in ("integer", "number"):
        m = _NUMBER_RE.search(s)
        if m:
            val = m.group(0)
            if "." in val:
                return str(float(val))
            return str(int(float(val)))
    if answer_type == "yes_no":
        if s in ("yes", "y", "true"):
            return "yes"
        if s in ("no", "n", "false"):
            return "no"
    return s


def parse_final_answer(response: str) -> str | None:
    text = (response or "").strip()
    if not text:
        return None
    m = _FINAL_ANSWER_RE.search(text)
    if m:
        return m.group(1).strip()
    # Fallback: last non-empty line
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        return lines[-1]
    return None


def split_explanation(response: str) -> str:
    text = response or ""
    m = _FINAL_ANSWER_RE.search(text)
    if m:
        return text[: m.start()].strip()
    return text.strip()


def score_row(row: dict[str, Any]) -> dict[str, Any]:
    answer_type = row.get("answer_type", "text")
    parsed_raw = parse_final_answer(row.get("response", ""))
    parsed = normalize_answer(parsed_raw, answer_type)
    gold = normalize_answer(row.get("gold_answer"), answer_type)
    return {
        "parsed_final_answer": parsed_raw,
        "parsed_normalized": parsed,
        "is_correct": bool(parsed) and parsed == gold,
        "explanation_text": split_explanation(row.get("response", "")),
    }
