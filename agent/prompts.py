"""Terse prompts. Every word sent is a billed token, so these stay minimal.

Track 1 ranks passing submissions by FEWEST tokens. Two levers:
  - short system prompt (sent with every task)
  - answer-only output (no preamble, no restating the question)

Most categories want a bare answer. Math/logic/code need a little room to be
correct - accuracy gate comes first, so we don't starve them.
"""

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
