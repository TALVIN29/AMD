"""The smart router: answer locally (free) where a small model is reliable, and
escalate to Fireworks only for the hard categories where it isn't.

The leaderboard rewards fewer Fireworks tokens, so we keep as much as possible on the
free local path. Easy categories (facts, sentiment, NER, summarisation) -> local.
Hard categories (math, logic, code) -> Fireworks, where accuracy matters most.
"""
from __future__ import annotations

import os

from agent import fireworks, local
from agent.prompts import infer_category, is_reasoning, system_for

# Preferred Fireworks model per task shape, matched by substring against
# whatever ALLOWED_MODELS the harness injects (exact IDs are launch-day only).
_CODE_MODEL_HINT = "kimi-k2p7-code"
_GENERAL_MODEL_HINT = "gemma-4-26b-a4b-it"

DRY_RUN = os.environ.get("AGENT_DRY_RUN") == "1"
# When a task has no category label, default to the free local path. Set to 1 to
# play safe and escalate unlabelled tasks to Fireworks instead.
ESCALATE_UNKNOWN = os.environ.get("ESCALATE_UNKNOWN", "0") == "1"


def route(prompt: str, category: str | None) -> tuple[str, str, int]:
    """Return (answer, route, fireworks_tokens). fireworks_tokens is 0 for local."""
    if category is None:
        category = infer_category(prompt)  # official example payload has no category field
    system = system_for(category)

    if DRY_RUN:
        return f"[dry-run: {prompt[:40]}]", "dry-run", 0

    escalate = is_reasoning(category) or (category is None and ESCALATE_UNKNOWN)
    if not escalate:
        return local.answer(prompt, system), "local", 0

    # Escalate to Fireworks; fall back to the local answer if the call fails so a
    # task is never dropped.
    try:
        remote_answer, tokens = fireworks.answer(prompt, model=_fireworks_model(category), system=system)
        return remote_answer, "remote", tokens
    except Exception:  # noqa: BLE001
        return local.answer(prompt, system), "local_fallback", 0


def _fireworks_model(category: str | None) -> str:
    """Pick the Fireworks escalation model: MODEL/REMOTE_MODEL override, else
    the best-fit model in ALLOWED_MODELS for this task (code-tuned model for
    code, a smaller/cheaper general model otherwise), else just first allowed."""
    override = os.environ.get("MODEL") or os.environ.get("REMOTE_MODEL")
    if override:
        return override
    raw = os.environ.get("ALLOWED_MODELS", "")
    models = [m.strip() for m in raw.split(",") if m.strip()]
    if not models:
        raise RuntimeError("ALLOWED_MODELS not set")

    is_code = bool(category) and category.strip().lower() in {
        "code_debugging", "code debugging", "code_generation", "code generation",
    }
    hint = _CODE_MODEL_HINT if is_code else _GENERAL_MODEL_HINT
    for m in models:
        if hint in m:
            return m
    return models[0]
