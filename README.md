# Token-Minimal Agent — AMD Hackathon Act II, Track 1

A one-shot agent that answers the 8 Track 1 task categories (facts, math, sentiment,
summarisation, named-entity recognition, code debugging, logic, code generation) using
**Fireworks AI** — spending as **few tokens** as possible while staying correct.

## How Track 1 is scored (why this design)

1. **Accuracy gate** — an LLM judge checks each answer. Below the bar → excluded.
2. **Token efficiency** — passing submissions are ranked by **fewest total Fireworks tokens**.

So there are exactly two levers, and this agent pulls both:

- **Terse prompts** — a short system prompt, no persona bloat (every word sent is billed).
- **Answer-only outputs** — no preamble or restating the question; brief working only where
  math/logic/code need it to stay correct. (See `agent/prompts.py`.)

> **All inference goes through `FIREWORKS_API_BASE_URL`.** The rules state local-model tokens
> count as zero and calls that bypass the Fireworks URL are not recorded — so there is no
> local-model answer path. (An earlier version of this repo answered locally to save dollar
> cost; that wins nothing here — the game is fewest *Fireworks* tokens, not lowest bill.)

## What the container does

The submission is a **batch job**, not a web server:

```
start → read /input/tasks.json → answer each task via Fireworks → write /output/results.json → exit 0
```

- `agent/run.py` — the entrypoint (`python -m agent.run`).
- `agent/fireworks.py` — the Fireworks (OpenAI-compatible) call; picks the smallest allowed
  model, escalates to the next only if a call fails.
- `agent/prompts.py` — the terse system prompts.
- `eval/` — practice dataset + a harness that reports **accuracy and total tokens** for tuning.

### Environment variables (injected by the judging harness)

| Variable | Meaning |
|----------|---------|
| `FIREWORKS_API_KEY` | Provided by the harness — use this, not your own |
| `FIREWORKS_API_BASE_URL` | Base URL all calls must go through |
| `ALLOWED_MODELS` | Comma-separated permitted model IDs, published on launch day |

Do not hardcode the key or model IDs — they are read from the environment at runtime.

## Build & run

```bash
# build the linux/amd64 image the judging VM needs
docker build --platform linux/amd64 -t <registry>/amd-track1:latest .

# smoke-test the plumbing with no API key (stub answers)
docker run --rm -e AGENT_DRY_RUN=1 \
  -v "$PWD/eval:/input:ro" -v "$PWD/out:/output" amd-track1:latest
# (rename eval/sample_tasks.json -> tasks.json in the mounted dir first)
```

Publish the image to a public registry (e.g. GHCR) and submit the pull URL.

## Tuning tokens (with your own Fireworks key)

```bash
export FIREWORKS_API_BASE_URL=https://api.fireworks.ai/inference/v1
export FIREWORKS_API_KEY=fw_...
export MODEL=accounts/fireworks/models/<some-allowed-model>
python -m eval.harness   # prints accuracy + total tokens; try smaller models / shorter prompts
```

## Launch-day checklist

- [ ] Confirm the real `ALLOWED_MODELS` list and pick the smallest model that passes each category.
- [ ] Confirm the exact `tasks.json` schema (this agent already handles `task_id`/`id` and
      `prompt`/`input`/`text`/`question`, and both list and `{"tasks": [...]}` shapes).
- [ ] Confirm whether a separate inference/token log is required and in what format
      (currently written to `/output/inference_log.jsonl` as a best guess).
- [ ] Confirm on Discord that a local model may be used only for routing, never for graded answers.

## License

MIT — see [LICENSE](LICENSE).
