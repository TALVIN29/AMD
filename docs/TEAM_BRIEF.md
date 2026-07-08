# Team Brief — what changed and what to do next

Short version for teammates. All plain English.

## The one thing to understand

Track 1 is a **"be correct while calling the paid AI as little as possible" contest**.
Judges first check our answers are right, then rank everyone by **how few tokens
(word-pieces) they spent on Fireworks AI**. Fewer = higher rank.

**The key rule (confirmed on launch day):** a **local** AI model running *inside our
container* is **free** — it counts toward being correct, but its tokens do **not** count
against us. The organizers literally say: *run as many local models as you need, and make
as few Fireworks calls as possible.* A submission that answers everything locally and calls
Fireworks zero times is a valid way to reach the **top** of the leaderboard.

## What our agent now does (a "smart router")

```
each task → small local model (free)  →  confident?  → use its answer   (0 tokens)
                                       →  unsure?     → ask Fireworks     (costs tokens)
```

- Easy tasks (facts, sentiment, names, summaries) → answered **locally for free**.
- Hard tasks (math, logic, code) → sent to **Fireworks** only when the small model isn't sure.

## What I changed (and one honest correction)

I first built a Fireworks-**only** version, because an **older** copy of the guide implied
all answers had to go through Fireworks. The **updated** guide flips that — local is free and
encouraged. So I rebuilt it the right way:

1. **Smart router**: try the free local model first, fall back to Fireworks only when unsure.
2. **Bundled a small local model** (a 2-3B "quantized" model via llama.cpp) that runs on the
   judging machine's modest hardware (4 GB RAM, 2 CPUs, no GPU).
3. **Kept it as a one-shot program** in the right shape: read tasks → answer → write results → stop.
4. **Terse prompts** so any Fireworks calls we *do* make stay cheap.

Our earlier Fireworks-only image is still a **valid backup** entry (correct, just spends
more tokens). The new one aims for a real leaderboard position.

## What still needs decisions (before the July 11 deadline)

- **Which local model + how eager to escalate.** There's a dial (`CONFIDENCE_THRESHOLD`):
  higher = safer answers but more Fireworks tokens; lower = cheaper but riskier. We tune it
  on practice tasks. See `README.md`.
- **Which Fireworks model** to fall back to (allowed list is in Discord).

## Your task: pressure-test it with Codex

I want a second pair of eyes. Please run **Codex** (OpenAI's coding agent) over the repo and
push back — find anything that loses accuracy, wastes Fireworks tokens, or breaks on the
4 GB / 2-CPU box.

### How to run Codex
1. Install (one-time): `npm install -g @openai/codex`
2. In a terminal, go into the repo folder and run: `codex`
3. Paste this prompt:

```
This repo is an AMD Hackathon Track 1 agent. Scoring: pass an LLM-judge accuracy gate,
then rank by FEWEST Fireworks tokens. Local model inference is FREE (doesn't count toward
tokens), so the agent is a router: answer locally, escalate to Fireworks only when unsure.
Grading box: 4 GB RAM, 2 vCPU, CPU-only, linux/amd64.

Review for improvements. Hard constraints — do NOT break these:
- Keep local-first routing; Fireworks is only the fallback (via FIREWORKS_BASE_URL / ALLOWED_MODELS).
- Must fit 4 GB RAM on CPU (local model stays 2-3B 4-bit); image under 10 GB; ready in 60s.
- One-shot batch: read /input/tasks.json, write valid /output/results.json (list of {task_id, answer}), exit 0.

Focus on:
1. The routing decision in agent/router.py — is the confidence signal from agent/local.py
   (avg token logprob) a sound escalation trigger? Suggest better, still-cheap signals.
2. Prompt wording in agent/prompts.py — shorter while keeping accuracy on all 8 categories?
3. Is a 2-3B model the right pick, or is there a better small model for math/logic/code?
4. Robustness of tasks.json parsing in agent/run.py against schema variants.

Propose concrete edits with expected impact on accuracy and token count. Don't over-engineer.
```

4. Bring whatever Codex suggests back to the group — we decide together what to keep.

> Codex needs its own OpenAI API key (`export OPENAI_API_KEY=...`). No key? Tell me.
