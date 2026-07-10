# Smart-Router Agent — AMD Hackathon Act II, Track 1

> 👋 **Teammates: start with [`docs/HANDOVER.md`](docs/HANDOVER.md)** — plain-English overview,
> status, and who-does-what. This README is the technical version.

Answers the 8 Track 1 categories (facts, math, sentiment, summarisation, NER, code
debugging, logic, code generation) while spending the **fewest Fireworks tokens** possible.

## The strategy (why this design)

Track 1 scoring: **(1)** pass an LLM-judge accuracy gate, then **(2)** rank by fewest
Fireworks tokens. Crucially, the updated rules say:

> *Local model inference inside the container is permitted and counts toward accuracy,
> but **not** toward the token score.* (FAQ Q22: "run as many local models as you need…
> make as few external API calls to Fireworks as possible.")

So the agent is a **smart router**, split by category:

```
easy categories (facts, sentiment, NER, summaries) → LOCAL model (2-3B, CPU)  → 0 tokens
hard categories (math, logic, code)                → Fireworks                → costs tokens
```

- **Local answers are free**, so every easy task costs zero tokens.
- **Fireworks handles the hard categories**, where a tiny model would likely fail the
  accuracy gate. If a Fireworks call fails, we fall back to the local answer so no task is dropped.
- An all-local run scoring `ZERO_API_CALLS` is an explicitly valid, top-rank strategy — so the
  more we can safely move to local, the better. Routing is category-based (deterministic,
  no per-token logprobs), which keeps memory within the 4 GB budget.

## Files

- `agent/run.py` — batch entrypoint (`python -m agent.run`).
- `agent/router.py` — local-first, escalate-by-category decision (with a text-based
  fallback guess when no category field is given).
- `agent/local.py` — the bundled GGUF model via llama.cpp (CPU).
- `agent/fireworks.py` — the Fireworks (OpenAI-compatible) escalation call.
- `agent/prompts.py` — terse prompts (shorter output = fewer tokens *and* faster CPU).
- `eval/` — practice dataset + a harness reporting accuracy, local/remote split, and tokens.

## The container

A **one-shot batch job** (not a web server), sized for the 4 GB / 2 vCPU / CPU-only grading box:

```
start → read /input/tasks.json → route each task → write /output/results.json → exit 0
```

`results.json` is a list of `{"task_id": ..., "answer": ...}` objects.

### Environment variables (injected by the harness)

| Variable | Meaning |
|----------|---------|
| `FIREWORKS_API_KEY` | Provided by the harness — use this, not your own |
| `FIREWORKS_BASE_URL` (or `FIREWORKS_API_BASE_URL`) | Base URL all Fireworks calls go through |
| `ALLOWED_MODELS` | Comma-separated permitted model IDs (published on launch day) |

Tunable knobs (sensible defaults): `MODEL` (force one Fireworks model), `ESCALATE_UNKNOWN`
(0 = answer unlabelled tasks locally), `LOCAL_MODEL_PATH`, `LLAMA_THREADS`, `LLAMA_CTX`.

## Build & run

```bash
# builds llama.cpp (CPU wheel) and bakes a 2-3B Q4 GGUF into the image
docker build --platform linux/amd64 -t <registry>/amd-track1:latest .

# smoke-test the plumbing with no model/key (stub answers)
docker run --rm -e AGENT_DRY_RUN=1 \
  -v "$PWD/eval:/input:ro" -v "$PWD/out:/output" amd-track1:latest
# (put a tasks.json in the mounted dir first)
```

Swap the local model with `--build-arg MODEL_URL=<hf gguf url>`.

## Tuning (once you have the models list + a Fireworks key)

```bash
export FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
export FIREWORKS_API_KEY=fw_...
export ALLOWED_MODELS=accounts/fireworks/models/<id>
export LOCAL_MODEL_PATH=./models/local.gguf   # download the GGUF locally to test
python -m eval.harness   # watch accuracy, local/remote split, and total tokens
```

Goal: **highest local-answer share that still clears the accuracy gate.** Every task the
local model handles is zero tokens.

## Launch-day checklist

- [ ] Pick the local model size that fits 4 GB and clears accuracy (2-3B Q4 recommended).
- [ ] Choose the cheapest Fireworks escalation model that passes (`MODEL` / `ALLOWED_MODELS`).
- [ ] Confirm the exact `tasks.json` schema (agent already handles common field/shape variants,
      and falls back to inferring category from the prompt text if no category field is present).

## License

MIT — see [LICENSE](LICENSE).
