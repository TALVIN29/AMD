"""Terse prompts. Every word sent is a billed token, so these stay minimal.

Track 1 ranks passing submissions by FEWEST tokens. Two levers:
  - short system prompt (sent with every task)
  - answer-only output (no preamble, no restating the question)

Most categories want a bare answer. Math/logic/code need a little room to be
correct - accuracy gate comes first, so we don't starve them.
"""
from __future__ import annotations

import re

# Default: applies to factual, sentiment, NER, summarisation.
DEFAULT = "Answer directly. No preamble, no explanation. Give only the answer."

# Categories that need brief working to stay correct (still no filler).
REASONING = "Solve it. Show minimal working, then end with the final answer on its own line."

# ponytail: one map, edit here once we see real category labels on launch day.
_REASONING_CATEGORIES = {
    "math", "mathematical_reasoning", "mathematical reasoning",
    "logic", "logical_reasoning", "logical / deductive reasoning",
    "code_debugging", "code debugging",
    "code_generation", "code generation",
}


def is_reasoning(category: str | None) -> bool:
    return bool(category) and category.strip().lower() in _REASONING_CATEGORIES


def system_for(category: str | None) -> str:
    return REASONING if is_reasoning(category) else DEFAULT


# The official Track 1 example payload omits `category` entirely (just
# task_id + prompt). If the real tasks.json does the same, routing needs a
# way to still catch math/logic/code without a label. Cheap keyword/regex
# check - no LLM call, no extra tokens - used only when category is missing.
_CODE_MARKERS = re.compile(
    r"```|\bdef \w+\(|\bfunction\s+\w+\s*\(|\bclass \w+[:(]|traceback|"
    r"syntaxerror|\bbug\b|fix this code|write a function|implement a function",
    re.IGNORECASE,
)
_MATH_MARKERS = re.compile(
    r"\d+\s*[%+\-*/^]\s*\d+|\bpercent(age)?\b|\bcalculate\b|\bhow many\b|"
    r"\bsum of\b|\baverage\b|\bsquare root\b",
    re.IGNORECASE,
)
_LOGIC_MARKERS = re.compile(
    r"\bif\b.+\bthen\b|\ball of the following\b|\bmust be true\b|puzzle|constraint",
    re.IGNORECASE,
)


def infer_category(prompt: str) -> str | None:
    """Fallback category guess from prompt text when no category field is given.
    Ambiguous prompts return None and fall through to the free local path,
    same as before - this only adds coverage, it never removes any."""
    if _CODE_MARKERS.search(prompt):
        return "code_generation"
    if _MATH_MARKERS.search(prompt):
        return "math"
    if _LOGIC_MARKERS.search(prompt):
        return "logic"
    return None
