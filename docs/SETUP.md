# Account & Submission Setup (do this before launch day)

Two accounts needed. Follow top to bottom. No coding — copy/paste only.

---

## 1. Fireworks AI (for testing our agent locally)

> The real evaluation injects its **own** Fireworks key — you don't submit yours.
> You only need a personal key to *test and tune* before launch day.

1. Go to **https://fireworks.ai** → **Sign up** (Google or email).
2. Open the dashboard → **API Keys** → **Create API Key**.
3. Copy the key (looks like `fw_xxxxxxxx`). Keep it private — treat it like a password.
4. Test it works (in a terminal, in the repo folder):
   ```bash
   export FIREWORKS_API_BASE_URL=https://api.fireworks.ai/inference/v1
   export FIREWORKS_API_KEY=fw_your_key_here
   export MODEL=accounts/fireworks/models/llama-v3p1-8b-instruct   # any current model
   python -m eval.harness
   ```
   You should see per-task answers + an accuracy/token summary.

---

## 2. GitHub Container Registry (GHCR) — to publish our Docker image

The submission is a Docker image URL that anyone can pull. We host it free on GHCR.

### a. Make a token (one-time)
1. GitHub → click your avatar → **Settings**.
2. Bottom left → **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
3. **Generate new token (classic)**. Name it `amd-hackathon`. Tick **`write:packages`**
   and **`read:packages`**. Generate. **Copy the token now** (shown once).

### b. Log Docker in (one-time, per machine)
```bash
docker login ghcr.io -u YOUR_GITHUB_USERNAME -p YOUR_TOKEN
```

### c. Build, push, make public
```bash
# from inside the repo folder
docker build --platform linux/amd64 -t ghcr.io/YOUR_GITHUB_USERNAME/amd-track1:latest .
docker push ghcr.io/YOUR_GITHUB_USERNAME/amd-track1:latest
```
Then make it public so judges can pull it:
1. GitHub → your avatar → **Your packages** → **amd-track1**.
2. **Package settings** → **Change visibility** → **Public**.

### d. Submit
Submit this pull URL on lablab:
```
ghcr.io/YOUR_GITHUB_USERNAME/amd-track1:latest
```

> Once you've done step **b** (`docker login`), Claude can run steps **c** and **d** for you —
> just say so. Never paste your token into chat; keep it in the terminal only.

---

## 3. Launch-day (when organizers reveal the models + task format)

1. Read the real `ALLOWED_MODELS` list. Try the **smallest** model first in `eval/harness.py`;
   only move up for math/logic/code if accuracy drops.
2. Confirm the exact `tasks.json` fields (our agent already handles the common variants).
3. Rebuild, push, submit (steps 2c–2d). Re-submit as you improve — 10 submissions/hour allowed.
