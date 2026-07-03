# Hybrid Token-Efficient Routing Agent

Built for **Track 1** of the AMD Developer Hackathon Act II. The agent decides, per task, whether
to answer with a cheap local model or escalate to a paid remote model - aiming to minimize cost
while staying above an accuracy threshold.

## How it works

```
Task input -> Local Gemma (AMD Developer Cloud / ROCm)
                 -> confidence check (avg token probability)
                     -> confident enough  -> return local answer   (cost ~ $0)
                     -> not confident     -> escalate to Fireworks-hosted Gemma -> return that answer
```

If the remote call fails, the router falls back to the local answer rather than failing the task.

- `router/` - local + remote model calls, confidence scoring, the routing decision (`router/cascade.py`)
- `eval/` - a practice dataset (`eval/dataset.jsonl`) and a harness (`eval/harness.py`) that reports
  accuracy and total cost, used to tune `CONFIDENCE_THRESHOLD`
- `service/` - a FastAPI wrapper exposing the router as an HTTP endpoint

## Setup

1. Copy `.env.example` to `.env` and fill in `FIREWORKS_API_KEY` (from your Fireworks AI account).
2. Local model inference expects a ROCm-enabled PyTorch build when running on the AMD Developer
   Cloud GPU instance - the `torch` pin in `requirements.txt` is a generic CPU/CUDA build for local
   dev; swap in AMD's ROCm wheel (see AMD Developer Cloud docs) before running on GPU.

### Run with Docker (recommended - matches the submission requirement)

```bash
docker compose up --build
```

The service is then available at `http://localhost:8000`.

### Run locally without Docker

```bash
pip install -r requirements.txt
uvicorn service.app:app --reload
```

## Usage

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```

Returns:

```json
{"answer": "Paris", "route": "local", "confidence": 0.94, "cost": 0.0}
```

## Evaluating / tuning the router

```bash
python -m eval.harness
```

Prints per-task routing decisions plus a summary of accuracy, total cost, and the local/remote
split. Use this to tune `CONFIDENCE_THRESHOLD` in `.env` before the real eval set is revealed.

## License

MIT - see [LICENSE](LICENSE).
