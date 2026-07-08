"""Tune the agent on the practice dataset: report accuracy AND total tokens.

Track 1 = pass the accuracy gate, then win on FEWEST tokens. So this measures both.
Point it at Fireworks with your own key while developing:

    export FIREWORKS_API_BASE_URL=https://api.fireworks.ai/inference/v1
    export FIREWORKS_API_KEY=fw_...
    export MODEL=accounts/fireworks/models/<some-allowed-model>
    python -m eval.harness

No key handy? `AGENT_DRY_RUN=1 python -m eval.harness` exercises the plumbing
(stub answers, 0 tokens) without calling the API.
"""
import json
from pathlib import Path

from agent import fireworks
from agent.prompts import system_for
from agent.run import allowed_models, field

DATASET_PATH = Path(__file__).parent / "dataset.jsonl"


def load_dataset():
    with open(DATASET_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def is_correct(answer: str, expected: str) -> bool:
    if expected == "open-ended":
        return True  # not exact-match gradable; excluded from strict scoring
    return expected.strip().lower() in answer.strip().lower()


def main():
    dataset = load_dataset()
    models = allowed_models()
    total_tokens = 0
    correct = 0
    gradable = 0

    for row in dataset:
        prompt = field(row, "prompt", "input", "text", "question")
        category = field(row, "category", "type") or None
        text, tokens = fireworks.answer(prompt, model=models[0], system=system_for(category))
        total_tokens += tokens
        if row.get("expected") != "open-ended":
            gradable += 1
            if is_correct(text, row["expected"]):
                correct += 1
        print(f"tokens={tokens:>4}  {prompt[:50]!r} -> {text[:50]!r}")

    print("\n--- Summary ---")
    print(f"Model: {models[0]}")
    print(f"Accuracy: {correct}/{gradable} gradable ({100 * correct / max(gradable, 1):.1f}%)")
    print(f"Total tokens: {total_tokens}  (lower = better rank)")


if __name__ == "__main__":
    main()
