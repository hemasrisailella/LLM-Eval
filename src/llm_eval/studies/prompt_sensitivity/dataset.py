from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# 30 reasoning problems (6 per category). Gold answers are unambiguous.
_BASE_PROBLEMS: list[dict[str, Any]] = [
    # --- arithmetic ---
    {
        "id": "arith_001",
        "base_question": "Jan has 3 times as many books as Tom. Tom has 12 books. How many books do they have together?",
        "gold_answer": "48",
        "category": "arithmetic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "arith_002",
        "base_question": "A train travels 60 miles in the first hour and 45 miles in the second hour. What is its average speed in miles per hour over the two hours?",
        "gold_answer": "52.5",
        "category": "arithmetic",
        "difficulty": "medium",
        "answer_type": "number",
    },
    {
        "id": "arith_003",
        "base_question": "A shirt costs $40. It is discounted by 25%. What is the sale price in dollars?",
        "gold_answer": "30",
        "category": "arithmetic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "arith_004",
        "base_question": "There are 4 boxes with 7 apples each. 5 apples are eaten. How many apples remain?",
        "gold_answer": "23",
        "category": "arithmetic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "arith_005",
        "base_question": "If 3 workers finish a job in 8 days, how many days would 6 workers take (same rate, working independently in parallel)?",
        "gold_answer": "4",
        "category": "arithmetic",
        "difficulty": "medium",
        "answer_type": "integer",
    },
    {
        "id": "arith_006",
        "base_question": "A number is doubled and then 10 is added. The result is 50. What was the original number?",
        "gold_answer": "20",
        "category": "arithmetic",
        "difficulty": "medium",
        "answer_type": "integer",
    },
    # --- logic ---
    {
        "id": "logic_001",
        "base_question": "Alice is taller than Bob. Bob is taller than Carol. Who is shortest?",
        "gold_answer": "Carol",
        "category": "logic",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "logic_002",
        "base_question": "All bloops are razzies. Some razzies are green. Can we conclude that some bloops are green? Answer yes or no.",
        "gold_answer": "no",
        "category": "logic",
        "difficulty": "medium",
        "answer_type": "yes_no",
    },
    {
        "id": "logic_003",
        "base_question": "Three people sit in a row. Ana is not at either end. Ben is to the right of Ana. Who sits in the middle?",
        "gold_answer": "Ana",
        "category": "logic",
        "difficulty": "medium",
        "answer_type": "text",
    },
    {
        "id": "logic_004",
        "base_question": "If it rains, the ground is wet. The ground is wet. Must it have rained? Answer yes or no.",
        "gold_answer": "no",
        "category": "logic",
        "difficulty": "medium",
        "answer_type": "yes_no",
    },
    {
        "id": "logic_005",
        "base_question": "Exactly one of A, B, C is true. A and B are false. Is C true? Answer yes or no.",
        "gold_answer": "yes",
        "category": "logic",
        "difficulty": "easy",
        "answer_type": "yes_no",
    },
    {
        "id": "logic_006",
        "base_question": "A clock shows 3:00. What is the smaller angle in degrees between the hour and minute hands?",
        "gold_answer": "90",
        "category": "logic",
        "difficulty": "medium",
        "answer_type": "integer",
    },
    # --- commonsense ---
    {
        "id": "cs_001",
        "base_question": "You drop a glass on a concrete floor. What is most likely to happen to the glass?",
        "gold_answer": "break",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "cs_002",
        "base_question": "It is winter in the Northern Hemisphere. Which way does water typically freeze first in a pond: at the surface or at the bottom?",
        "gold_answer": "surface",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "cs_003",
        "base_question": "A car runs out of fuel on a level road. Without pushing, will it keep moving forever? Answer yes or no.",
        "gold_answer": "no",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "yes_no",
    },
    {
        "id": "cs_004",
        "base_question": "You leave ice cream in direct sunlight on a hot day. What happens to its temperature?",
        "gold_answer": "increases",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "cs_005",
        "base_question": "A plant is kept in a completely dark closet with no water for two weeks. Is it more likely to grow or wilt?",
        "gold_answer": "wilt",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "cs_006",
        "base_question": "You stir sugar into hot tea until none is visible. Where did the sugar go?",
        "gold_answer": "dissolved",
        "category": "commonsense",
        "difficulty": "easy",
        "answer_type": "text",
    },
    # --- symbolic ---
    {
        "id": "sym_001",
        "base_question": "What is the next letter in the sequence: A, C, E, G, ?",
        "gold_answer": "I",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "text",
    },
    {
        "id": "sym_002",
        "base_question": "What is the next number in the sequence: 2, 4, 8, 16, ?",
        "gold_answer": "32",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "sym_003",
        "base_question": "If A=1, B=2, C=3, what is the sum of the letter values in CAB?",
        "gold_answer": "6",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "sym_004",
        "base_question": "Solve for x: 2x + 5 = 17",
        "gold_answer": "6",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "sym_005",
        "base_question": "What is the next symbol in the pattern: ○, ○○, ○○○, ? (give the count of circles as a number)",
        "gold_answer": "4",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "integer",
    },
    {
        "id": "sym_006",
        "base_question": "Reverse the word LIST. What is the result?",
        "gold_answer": "TSIL",
        "category": "symbolic",
        "difficulty": "easy",
        "answer_type": "text",
    },
    # --- trick / bias-sensitive ---
    {
        "id": "trick_001",
        "base_question": "A bat and ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost in dollars?",
        "gold_answer": "0.05",
        "category": "trick",
        "difficulty": "hard",
        "answer_type": "number",
    },
    {
        "id": "trick_002",
        "base_question": "How many animals of each kind did Moses take on the Ark? If the question is flawed, answer 'invalid'; otherwise give a number.",
        "gold_answer": "invalid",
        "category": "trick",
        "difficulty": "medium",
        "answer_type": "text",
    },
    {
        "id": "trick_003",
        "base_question": "If you pass the person in second place in a race, what place are you in now?",
        "gold_answer": "second",
        "category": "trick",
        "difficulty": "medium",
        "answer_type": "text",
    },
    {
        "id": "trick_004",
        "base_question": "A farmer has 17 sheep. All but 9 die. How many sheep are left alive?",
        "gold_answer": "9",
        "category": "trick",
        "difficulty": "medium",
        "answer_type": "integer",
    },
    {
        "id": "trick_005",
        "base_question": "How many times can you subtract 5 from 25?",
        "gold_answer": "1",
        "category": "trick",
        "difficulty": "hard",
        "answer_type": "integer",
    },
    {
        "id": "trick_006",
        "base_question": "Which weighs more: a pound of feathers or a pound of bricks?",
        "gold_answer": "same",
        "category": "trick",
        "difficulty": "easy",
        "answer_type": "text",
    },
]


def load_styles(styles_path: Path) -> dict[str, str]:
    with styles_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_problem_records(
    categories: list[str] | None = None,
    per_category: int = 6,
) -> list[dict[str, Any]]:
    cats = set(categories or [])
    records = []
    counts: dict[str, int] = {}
    for p in _BASE_PROBLEMS:
        if cats and p["category"] not in cats:
            continue
        n = counts.get(p["category"], 0)
        if n >= per_category:
            continue
        records.append(dict(p))
        counts[p["category"]] = n + 1
    return records


def expand_prompt_items(
    problems: list[dict[str, Any]],
    styles: dict[str, str],
    style_order: list[str],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for prob in problems:
        for style_id in style_order:
            if style_id not in styles:
                raise KeyError(f"Missing style in styles.yaml: {style_id}")
            wrapper = styles[style_id].format(base_question=prob["base_question"])
            items.append(
                {
                    "id": f"{prob['id']}__{style_id}",
                    "problem_id": prob["id"],
                    "prompt_style": style_id,
                    "base_question": prob["base_question"],
                    "question": wrapper.strip(),
                    "gold_answer": prob["gold_answer"],
                    "category": prob["category"],
                    "difficulty": prob["difficulty"],
                    "answer_type": prob["answer_type"],
                }
            )
    return items


def build_datasets(
    styles_path: Path,
    style_order: list[str],
    categories: list[str] | None = None,
    per_category: int = 6,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    styles = load_styles(styles_path)
    problems = build_problem_records(categories=categories, per_category=per_category)
    questions = expand_prompt_items(problems, styles, style_order)
    return problems, questions
