"""Fireworks AI call (OpenAI-compatible) for escalated tasks."""
import os
import requests

# ponytail: requests is the one dependency; stdlib urllib would also work but
# requests gives us clean timeouts/retries for free.

DRY_RUN = os.environ.get("AGENT_DRY_RUN") == "1"


def _base_url() -> str:
    # The guide is inconsistent on the exact name, so accept both.
    url = (os.environ.get("FIREWORKS_BASE_URL") or os.environ.get("FIREWORKS_API_BASE_URL") or "").rstrip("/")
    if not url:
        raise RuntimeError("FIREWORKS base URL not set (harness injects it at eval time)")
    return url


def answer(prompt: str, model: str, system: str, max_tokens: int = 512) -> tuple[str, int]:
    """Return (answer_text, total_tokens). Raises on HTTP failure so the caller
    can retry with a fallback model."""
    if DRY_RUN:
        # No network, no key: echo a stub so we can test the batch plumbing + Docker.
        return f"[dry-run answer to: {prompt[:40]}]", 0

    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    if not api_key:
        raise RuntimeError("FIREWORKS_API_KEY not set")

    resp = requests.post(
        _base_url() + "/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
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
