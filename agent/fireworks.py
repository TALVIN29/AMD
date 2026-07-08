"""Fireworks AI call (OpenAI-compatible). All graded inference goes through here.

Track 1 rule: every answer MUST go through FIREWORKS_API_BASE_URL, or it is not
recorded and scores zero. So there is no local-model path here on purpose.
"""
import os
import requests

# ponytail: requests is the one dependency; stdlib urllib would also work but
# requests gives us clean timeouts/retries for free.

DRY_RUN = os.environ.get("AGENT_DRY_RUN") == "1"


def _base_url() -> str:
    url = os.environ.get("FIREWORKS_API_BASE_URL", "").rstrip("/")
    if not url:
        raise RuntimeError("FIREWORKS_API_BASE_URL not set (harness injects it at eval time)")
    return url


def answer(prompt: str, model: str, system: str, max_tokens: int = 512) -> tuple[str, int]:
    """Return (answer_text, total_tokens). Raises on HTTP failure so the caller
    can retry with a fallback model."""
    if DRY_RUN:
        # No network, no key: echo a stub so we can test the batch plumbing + Docker.
        return f"[dry-run answer to: {prompt[:40]}]", 0

    resp = requests.post(
        _base_url() + "/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('FIREWORKS_API_KEY', '')}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"].strip()
    total_tokens = data.get("usage", {}).get("total_tokens", 0)
    return text, total_tokens
