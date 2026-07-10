"""Track 1 batch entrypoint.

Contract (from the participant guide):
  - read tasks from /input/tasks.json on startup
  - answer each (local model first, escalate to Fireworks only when unsure)
  - write /output/results.json: a list of {"task_id", "answer"} objects
  - exit 0 on success, non-zero on failure; total runtime <= 10 min

Run: python -m agent.run
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from agent import router

INPUT_PATH = Path(os.environ.get("INPUT_PATH", "/input/tasks.json"))
OUTPUT_PATH = Path(os.environ.get("OUTPUT_PATH", "/output/results.json"))
LOG_PATH = Path(os.environ.get("LOG_PATH", "/output/inference_log.jsonl"))


def load_tasks(raw: dict | list) -> list[dict]:
    """Accept a bare list or a {"tasks": [...]} wrapper - exact schema is only
    confirmed on launch day, so stay defensive."""
    if isinstance(raw, dict) and "tasks" in raw:
        raw = raw["tasks"]
    if isinstance(raw, list):
        if not all(isinstance(task, dict) for task in raw):
            raise ValueError("tasks.json must contain task objects")
        return raw
    raise ValueError(f"Unexpected tasks.json shape: {type(raw).__name__}")


def field(task: dict, *names: str, default: str = "") -> str:
    for n in names:
        if task.get(n) not in (None, ""):
            return str(task[n])
    return default


def main() -> int:
    raw = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    tasks = load_tasks(raw)

    results, log = [], []
    for i, task in enumerate(tasks):
        tid = field(task, "task_id", "id", default=str(i))
        prompt = field(task, "prompt", "input", "text", "question", "task")
        category = field(task, "category", "type") or None
        try:
            answer, route, tokens = router.route(prompt, category)
        except Exception as e:  # noqa: BLE001 - never drop a task; empty answer keeps JSON valid
            print(f"  task {tid} failed: {e}", file=sys.stderr)
            answer, route, tokens = "", "error", 0
        results.append({"task_id": tid, "answer": answer})
        log.append({"task_id": tid, "route": route, "fireworks_tokens": tokens})
        print(f"[{i + 1}/{len(tasks)}] {tid}: {route}, {tokens} tokens")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # results.json is a bare list of {task_id, answer} - the schema the judge checks.
    OUTPUT_PATH.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")

    # ponytail: routing/token log kept in a separate file so it can never corrupt
    # results.json. Not known to be required; handy for tuning the threshold.
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.write_text("\n".join(json.dumps(r) for r in log), encoding="utf-8")
    except Exception:
        pass

    total = sum(r["fireworks_tokens"] for r in log)
    n_remote = sum(1 for r in log if r["route"] == "remote")
    print(f"Done. {len(results)} answers, {n_remote} escalated, {total} Fireworks tokens -> {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
