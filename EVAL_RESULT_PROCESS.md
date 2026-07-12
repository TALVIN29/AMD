# Eval Result Process

This note documents how the practice eval result used in the submission deck was produced.
It is safe to commit because it does not contain any Fireworks API key.

## Goal

Run the local practice harness and capture the real result numbers for the Results slide:

- Accuracy
- Fireworks token usage
- Local vs paid routing split
- Docker image size

## Environment

Repository folder:

```bash
/Users/thoochinfeng/Desktop/AMD
```

Required local files:

```bash
README.md
docs/SETUP.md
eval/harness.py
models/local.gguf
```

The local model file used by the harness was:

```bash
models/local.gguf
```

## Fireworks Setup

The Fireworks API key was set only in the terminal environment. Do not write the real key into
any committed file.

```bash
export FIREWORKS_API_BASE_URL=https://api.fireworks.ai/inference/v1
export FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
export FIREWORKS_API_KEY=fw_your_real_key_here
export MODEL=accounts/fireworks/models/gpt-oss-120b
export LOCAL_MODEL_PATH=./models/local.gguf
```

The model was selected from the account-accessible Fireworks model list. Earlier attempts with
`accounts/fireworks/models/llama-v3p1-8b-instruct` returned `404 Model not found`, so the eval was
rerun with an accessible model.

## Command Run

From the repository root:

```bash
cd /Users/thoochinfeng/Desktop/AMD
source .venv/bin/activate
python -m eval.harness
```

## Harness Behavior

The harness loads the practice dataset from:

```bash
eval/dataset.jsonl
```

For each task, it calls:

```python
router.route(prompt, category)
```

The router answers easy tasks with the local GGUF model for zero Fireworks tokens. It routes
harder reasoning/code/math tasks to Fireworks, then records the returned token usage.

## Captured Output

The terminal summary from the successful run was:

```text
--- Summary ---
Accuracy: 8/9 gradable (88.9%)
Answered locally: 8/10  (free)
Total Fireworks tokens: 237  (lower = better rank)
```

## Numbers Used In The Slide Deck

| Metric | Value |
| --- | --- |
| Accuracy | 8/9 gradable (88.9%) |
| Total Fireworks tokens | 237 |
| Local answers | 8/10 |
| Paid Fireworks routes | 2/10 |
| Docker image size | 4.15GB under 10GB |

## Notes For Reproduction

- Do not commit `FIREWORKS_API_KEY`.
- Do not commit `models/local.gguf`; it is a local runtime artifact.
- If Fireworks returns `404 Model not found`, list accessible models for the account and set
  `MODEL` to one of those model IDs.
- If the local model fails to initialize on macOS because of `llama_context` or Metal backend
  errors, rerun on the intended Docker/Linux CPU environment or rebuild `llama-cpp-python` for a
  CPU-only local environment.

