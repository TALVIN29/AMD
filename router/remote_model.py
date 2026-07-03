"""Remote (paid) model call via the Fireworks AI API (OpenAI-compatible endpoint)."""
import requests

from router.config import FIREWORKS_API_KEY, REMOTE_MODEL

FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

# TODO: replace with Fireworks' published per-token price for REMOTE_MODEL.
PRICE_PER_1K_TOKENS = 0.0002


def answer(prompt: str, max_new_tokens: int = 256) -> tuple[str, int]:
    """Returns (answer_text, total_tokens_billed). Raises on failure - caller decides fallback."""
    resp = requests.post(
        FIREWORKS_URL,
        headers={"Authorization": f"Bearer {FIREWORKS_API_KEY}"},
        json={
            "model": REMOTE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    total_tokens = data.get("usage", {}).get("total_tokens", 0)
    return text.strip(), total_tokens


def cost_for_tokens(total_tokens: int) -> float:
    return (total_tokens / 1000) * PRICE_PER_1K_TOKENS
