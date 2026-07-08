"""Tune the router on the practice dataset: accuracy AND Fireworks tokens.

Winning Track 1 = clear the accuracy gate, then spend the fewest Fireworks tokens.
Local answers are free, so watch the local/remote split too.

    # needs the bundled GGUF present + Fireworks env for escalation
    export FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
    export FIREWORKS_API_KEY=fw_...
    export ALLOWED_MODELS=accounts/fireworks/models/<id>
    export LOCAL_MODEL_PATH=./models/local.gguf
    python -m eval.harness

No model/key? `AGENT_DRY_RUN=1 python -m eval.harness` checks the plumbing only.
"""
import json
from pathlib import Path

from agent import router
from agent.run import field

DATASET_PATH = Path(__file__).parent / "dataset.jsonl"


def load_dataset():
    with open(DATASET_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_correct(answer: str, expected: str) -> bool:
    if expected == "open-ended":
        return True  # not exact-match gradable
    return expected.strip().lower() in answer.strip().lower()


def main():
    dataset = load_dataset()
    total_tokens = correct = gradable = local_n = 0

    for row in dataset:
        prompt = field(row, "prompt", "input", "text", "question")
        category = field(row, "category", "type") or None
        answer, route, tokens = router.route(prompt, category)
        total_tokens += tokens
        if route.startswith("local"):
            local_n += 1
        if row.get("expected") != "open-ended":
            gradable += 1
            correct += is_correct(answer, row["expected"])
        print(f"[{route:>13}] tok={tokens:>4}  {prompt[:45]!r} -> {answer[:45]!r}")

    n = len(dataset)
    print("\n--- Summary ---")
    print(f"Accuracy: {correct}/{gradable} gradable ({100 * correct / max(gradable, 1):.1f}%)")
    print(f"Answered locally: {local_n}/{n}  (free)")
    print(f"Total Fireworks tokens: {total_tokens}  (lower = better rank)")


if __name__ == "__main__":
    main()
