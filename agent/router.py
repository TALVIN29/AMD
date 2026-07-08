"""The smart router: answer locally (free) where a small model is reliable, and
escalate to Fireworks only for the hard categories where it isn't.

The leaderboard rewards fewer Fireworks tokens, so we keep as much as possible on the
free local path. Easy categories (facts, sentiment, NER, summarisation) -> local.
Hard categories (math, logic, code) -> Fireworks, where accuracy matters most.
"""
import os

from agent import fireworks, local
from agent.prompts import is_reasoning, system_for

DRY_RUN = os.environ.get("AGENT_DRY_RUN") == "1"
# When a task has no category label, default to the free local path. Set to 1 to
# play safe and escalate unlabelled tasks to Fireworks instead.
ESCALATE_UNKNOWN = os.environ.get("ESCALATE_UNKNOWN", "0") == "1"


def route(prompt: str, category: str | None) -> tuple[str, str, int]:
    """Return (answer, route, fireworks_tokens). fireworks_tokens is 0 for local."""
    system = system_for(category)

    if DRY_RUN:
        return f"[dry-run: {prompt[:40]}]", "dry-run", 0

    escalate = is_reasoning(category) or (category is None and ESCALATE_UNKNOWN)
    if not escalate:
        return local.answer(prompt, system), "local", 0

    # Escalate to Fireworks; fall back to the local answer if the call fails so a
    # task is never dropped.
    try:
        remote_answer, tokens = fireworks.answer(prompt, model=_fireworks_model(), system=system)
        return remote_answer, "remote", tokens
    except Exception:  # noqa: BLE001
        return local.answer(prompt, system), "local_fallback", 0


def _fireworks_model() -> str:
    """Pick the Fireworks escalation model: MODEL override, else first allowed."""
    override = os.environ.get("MODEL")
    if override:
        return override
    raw = os.environ.get("ALLOWED_MODELS", "")
    models = [m.strip() for m in raw.split(",") if m.strip()]
    if not models:
        raise RuntimeError("ALLOWED_MODELS not set")
    return models[0]
