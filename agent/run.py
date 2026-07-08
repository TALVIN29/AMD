"""Track 1 batch entrypoint.

Contract (from the participant guide):
  - read tasks from /input/tasks.json on startup
  - answer each via Fireworks (all inference through FIREWORKS_API_BASE_URL)
  - write /output/results.json (valid JSON, or the submission scores zero)
  - exit 0 on success, non-zero on failure; total runtime <= 10 min

Run: python -m agent.run
"""
import json
import os
import sys
from pathlib import Path

from agent import fireworks
from agent.prompts import system_for

INPUT_PATH = Path(os.environ.get("INPUT_PATH", "/input/tasks.json"))
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", "/output/results.json"))
LOG_PATH = Path(os.environ.get("LOG_PATH", "/output/inference_log.jsonl"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "512"))


def allowed_models() -> list[str]:
    """Permitted Fireworks model IDs, published on launch day via ALLOWED_MODELS.
    MODEL env overrides for local testing."""
    override = os.environ.get("MODEL")
    if override:
        return [override]
    raw = os.environ.get("ALLOWED_MODELS", "")
    models = [m.strip() for m in raw.split(",") if m.strip()]
    if not models and not fireworks.DRY_RUN:
        raise RuntimeError("ALLOWED_MODELS not set (harness injects it on launch day)")
    return models or ["dry-run-model"]


def load_tasks(raw: dict | list) -> tuple[list[dict], bool]:
    """Return (tasks, wrapped). `wrapped` True if input was {"tasks": [...]} so we
    can mirror the shape on output. Handles a few field-name variants defensively
    since the exact schema is only confirmed on launch day."""
    if isinstance(raw, dict) and "tasks" in raw:
        return raw["tasks"], True
    if isinstance(raw, list):
        return raw, False
    raise ValueError(f"Unexpected tasks.json shape: {type(raw).__name__}")


def field(task: dict, *names: str, default: str = "") -> str:
    for n in names:
        if task.get(n) not in (None, ""):
            return task[n]
    return default


def answer_task(task: dict, models: list[str]) -> tuple[str, int]:
    prompt = field(task, "prompt", "input", "text", "question")
    category = field(task, "category", "type") or None
    system = system_for(category)
    last_err = None
    for model in models:  # smallest first; escalate on failure
        try:
            return fireworks.answer(prompt, model=model, system=system, max_tokens=MAX_TOKENS)
        except Exception as e:  # noqa: BLE001 - never crash the whole batch on one task
            last_err = e
    print(f"  all models failed for task: {last_err}", file=sys.stderr)
    return "", 0


def main() -> int:
    models = allowed_models()
    raw = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    tasks, wrapped = load_tasks(raw)

    results, log = [], []
    for i, task in enumerate(tasks):
        tid = field(task, "task_id", "id", default=str(i))
        text, tokens = answer_task(task, models)
        results.append({"task_id": tid, "answer": text})
        log.append({"task_id": tid, "total_tokens": tokens})
        print(f"[{i + 1}/{len(tasks)}] {tid}: {tokens} tokens")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"results": results} if wrapped else results
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    # ponytail: token log is a guess at the Track 1 "inference log" requirement -
    # separate file so it can never corrupt results.json. Verify format on launch day.
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.write_text("\n".join(json.dumps(r) for r in log), encoding="utf-8")
    except Exception:
        pass

    total = sum(r["total_tokens"] for r in log)
    print(f"Done. {len(results)} answers, {total} total tokens -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
