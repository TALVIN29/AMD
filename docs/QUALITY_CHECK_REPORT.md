# AMD Smart Router Quality Check Report

Date: 2026-07-09
Project path: `/Users/chris/Documents/AMD`
Repository: `TALVIN29/AMD`

## Executive Verdict

The project is structurally ready for submission.

Docker build, Docker run, mounted `/input/tasks.json` to `/output/results.json`, output JSON format, and router token-saving behavior were all checked successfully.

The main caveat is that the Docker run shown in the final checklist used `AGENT_DRY_RUN=1`, so it proves the container and input/output plumbing, not real answer quality. A separate real model smoke test was also run earlier and produced a valid answer under constrained Docker resources.

## Overall Result

Status: PASS with caveats

Ready for grading environment: Yes, assuming the grader provides the required Fireworks environment variables and the incoming task categories match the router's expected labels.

## Step 4: Test With Docker

Docker image build command:

```bash
docker build --platform linux/amd64 -t amd-smart-router .
```

Result: PASS

The image built successfully as `amd-smart-router:latest`.

Docker run command:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD/input:/input:ro" \
  -v "$PWD/output:/output" \
  -e AGENT_DRY_RUN=1 \
  amd-smart-router
```

Result: PASS

Observed output:

```text
[1/3] t1: dry-run, 0 tokens
[2/3] t2: dry-run, 0 tokens
[3/3] t3: dry-run, 0 tokens
Done. 3 answers, 0 escalated, 0 Fireworks tokens -> /output/results.json
```

The container exited successfully and created:

```text
output/results.json
```

The output file contained a valid list of result objects:

```json
[
  {
    "task_id": "t1",
    "answer": "[dry-run: What is the capital of France?]"
  },
  {
    "task_id": "t2",
    "answer": "[dry-run: What is 12 * 8?]"
  },
  {
    "task_id": "t3",
    "answer": "[dry-run: Classify sentiment: 'I love this.']"
  }
]
```

Required grading shape:

```json
[
  {
    "task_id": "some-id",
    "answer": "answer here"
  }
]
```

Result format: PASS

## Step 5: Check Token Usage

The router was checked directly inside Docker with local and Fireworks calls mocked, because `AGENT_DRY_RUN=1` intentionally bypasses real routing.

Observed routing:

| Task type | Observed route | Expected route | Result |
| --- | --- | --- | --- |
| sentiment | local | local | PASS |
| ner | local | local | PASS |
| summarisation | local | local | PASS |
| factual | local | local | PASS |
| math | remote / Fireworks | Fireworks | PASS |
| logic | remote / Fireworks | Fireworks | PASS |
| code_debugging | remote / Fireworks | Fireworks | PASS |
| code_generation | remote / Fireworks | Fireworks | PASS |

Summary:

```text
local routes: 4
remote routes: 4
easy tasks accidentally sent to Fireworks: no
hard tasks accidentally kept local: no
```

Verdict: PASS

## Step 6: Final Submission Safety

Safety checks performed:

| Check | Result |
| --- | --- |
| `.env` is not committed | PASS |
| Real API keys are not committed | PASS |
| Large model files are not committed | PASS |
| Docker command works | PASS |
| `results.json` format is correct | PASS |
| README instructions are aligned with current code | PASS after minor documentation fix |
| Local test artifacts are ignored | PASS after `.gitignore` update |

The secret scan only found placeholder examples such as:

```text
FIREWORKS_API_KEY=fw_...
FIREWORKS_API_KEY=fw_your_key_here
```

No real Fireworks or OpenAI-style keys were found.

No committed model files were found with extensions such as:

```text
.gguf
.safetensors
.bin
.pt
.pth
```

## Critical Fixes Applied

The following fixes were applied during the quality check process:

| File | Purpose |
| --- | --- |
| `.env.example` | Updated environment variable names to match what the code actually reads. |
| `.gitignore` | Added `input/`, `output/`, and `out/` so local test artifacts are not accidentally committed. |
| `Dockerfile` | Removed hard-coded `FROM --platform=linux/amd64`; platform is now supplied in the Docker build command. |
| `README.md` | Removed stale references to nonexistent threshold variables. |
| `docs/TEAM_BRIEF.md` | Updated router tuning notes to match the current category-based router. |
| `agent/run.py` | Added Python 3.9-safe annotations, task-object validation, string field normalization, and support for `task` prompt fields. |
| `agent/router.py` | Added Python 3.9-safe annotations and allowed `REMOTE_MODEL` as a legacy fallback for model selection. |
| `agent/prompts.py` | Added Python 3.9-safe annotations. |
| `agent/fireworks.py` | Added fail-fast handling for missing `FIREWORKS_API_KEY` and corrected misleading Fireworks-only wording. |

## Known Caveats

1. The final Docker checklist run used `AGENT_DRY_RUN=1`.
   This confirms Docker and file flow, but it does not measure real model accuracy.

2. Real Fireworks API behavior requires a local `.env` or grader-provided environment with:

```bash
FIREWORKS_API_KEY=...
FIREWORKS_API_BASE_URL=https://api.fireworks.ai/inference/v1
ALLOWED_MODELS=accounts/fireworks/models/...
```

3. The local Mac shell does not have a global `python` command, but the project venv provides one after activation:

```bash
source .venv/bin/activate
python -m agent.run
```

4. Native grading performance may differ from local Docker on Apple Silicon because local Docker runs `linux/amd64` through emulation.

## Recommended Final Test Before Submission

If a real Fireworks key and allowed model list are available, run:

```bash
docker run --rm --platform linux/amd64 \
  -v "$PWD/input:/input:ro" \
  -v "$PWD/output:/output" \
  --env-file .env \
  amd-smart-router
```

Then check:

```bash
python3 -m json.tool output/results.json
cat output/inference_log.jsonl
```

Expected result:

```text
Docker exits 0.
output/results.json exists.
Each result has task_id and answer.
Easy tasks route local.
Hard tasks route remote only when needed.
```

## Final Recommendation

Proceed with submission after confirming the real `.env` values or ensuring the grading platform injects them.

The project passes the important structural checks:

- Docker image builds.
- Container runs.
- `/input/tasks.json` is read.
- `/output/results.json` is written.
- Result JSON format is correct.
- Router saves Fireworks tokens for easy tasks.
- No secrets or large model files are committed.

