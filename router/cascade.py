"""The routing decision: try the cheap local model first, escalate only when unsure.

This is the piece the leaderboard actually grades - keep it legible.
"""
from router import local_model, remote_model
from router.config import CONFIDENCE_THRESHOLD


def route(prompt: str) -> dict:
    """Returns a dict describing the answer and how it was produced:
    {"answer": str, "route": "local"|"remote", "confidence": float, "cost": float}
    """
    local_answer, confidence = local_model.answer(prompt)

    if confidence >= CONFIDENCE_THRESHOLD:
        return {"answer": local_answer, "route": "local", "confidence": confidence, "cost": 0.0}

    try:
        remote_answer, total_tokens = remote_model.answer(prompt)
        return {
            "answer": remote_answer,
            "route": "remote",
            "confidence": confidence,
            "cost": remote_model.cost_for_tokens(total_tokens),
        }
    except Exception:
        # Fireworks call failed - never fail the task outright, return what we have.
        return {"answer": local_answer, "route": "local_fallback", "confidence": confidence, "cost": 0.0}
