"""Run the cascade router over the practice dataset and report accuracy vs. cost.

Usage: python -m eval.harness
"""
import json
from pathlib import Path

from router.cascade import route

DATASET_PATH = Path(__file__).parent / "dataset.jsonl"


def load_dataset():
    with open(DATASET_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def is_correct(answer: str, expected: str) -> bool:
    if expected == "open-ended":
        return True  # not exact-match gradable; excluded from strict scoring
    return expected.strip().lower() in answer.strip().lower()


def main():
    dataset = load_dataset()
    total_cost = 0.0
    correct = 0
    local_count = 0

    for row in dataset:
        result = route(row["prompt"])
        total_cost += result["cost"]
        if result["route"].startswith("local"):
            local_count += 1
        if is_correct(result["answer"], row["expected"]):
            correct += 1
        print(f"[{result['route']:>13}] conf={result['confidence']:.2f} cost=${result['cost']:.5f}  {row['prompt'][:60]}")

    n = len(dataset)
    print("\n--- Summary ---")
    print(f"Accuracy: {correct}/{n} ({100 * correct / n:.1f}%)")
    print(f"Total cost: ${total_cost:.5f}")
    print(f"Routed locally: {local_count}/{n} ({100 * local_count / n:.1f}%)")


if __name__ == "__main__":
    main()
