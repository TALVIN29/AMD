"""Config for the router, driven entirely by env vars so nothing is hardcoded."""
import os

LOCAL_MODEL = os.environ.get("LOCAL_MODEL", "google/gemma-2-2b-it")
REMOTE_MODEL = os.environ.get("REMOTE_MODEL", "accounts/fireworks/models/gemma2-9b-it")
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY", "")

# Confidence threshold: below this, escalate to the remote model.
# Tune this against eval/dataset.jsonl once the pipeline runs end-to-end.
CONFIDENCE_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.6"))
