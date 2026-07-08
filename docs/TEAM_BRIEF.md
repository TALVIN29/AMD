# Team Brief — what changed and what to do next

Short version for teammates. All plain English.

## The one thing to understand

Track 1 is a **"be correct using the fewest words" contest**. Judges first check our
answers are right, then rank everyone by **how few tokens (word-pieces) they spent on
Fireworks AI**. Fewer = higher rank.

## What our repo used to do (and why it was wrong)

The old version answered questions with a **local** model to save money, and only asked
the paid Fireworks model when unsure.

The rules say:
- Local answers **count as zero** — they win nothing.
- **Every answer must go through Fireworks** (`FIREWORKS_API_BASE_URL`), or it isn't recorded.

So the old "save money locally" idea scored nothing and risked disqualification. It also
was built as an always-on web app, but the contest wants a program that runs once and stops.

## What I changed

1. **Rebuilt it as a one-shot program**: read the tasks file → answer each with Fireworks →
   write the answers file → stop. (This is exactly the shape the contest asks for.)
2. **Made every prompt and answer as short as possible** — that's how you win the token game.
   (This is the same idea as the `caveman` and `ponytail` projects we studied.)
3. **Deleted the heavy local-model code** → our Docker image dropped from multiple GB to
   **208 MB** (limit is 10 GB), so it builds and uploads fast.
4. **Upgraded our test tool** to show accuracy **and** token count, so we can tune.

All of this is already **pushed to `main`**. Read `README.md` for the technical detail and
`docs/SETUP.md` for account setup.

## What still needs a human decision (launch day)

- The real list of allowed models + the exact task format are revealed on launch day.
  The code reads them at runtime — we just tune which model to use.
- **Ask on the lablab Discord**: *"For Track 1, can a local model be used only to route/decide,
  never to produce the graded answer?"* — confirms we're reading the rule right.

---

## Your task: pressure-test it with Codex

I want a second pair of eyes. Please run **Codex** (OpenAI's coding agent) over the repo and
push back on my work — find anything that loses accuracy or wastes tokens.

### How to run Codex
1. Install (one-time): `npm install -g @openai/codex`
2. In a terminal, go into the repo folder and run: `codex`
3. Paste this prompt:

```
This repo is an AMD Hackathon Track 1 agent. Scoring: pass an LLM-judge accuracy
gate, then rank by FEWEST total Fireworks tokens. Review it for improvements.

Hard constraints — do NOT break these:
- All graded inference must go through FIREWORKS_API_BASE_URL. Never add a local-model
  answer path (local tokens count as zero and are disallowed as final answers).
- Keep the Docker image small (no torch/transformers/heavy deps).
- Output must be a one-shot batch: read /input/tasks.json, write valid /output/results.json, exit 0.

Focus your review on:
1. Prompt wording in agent/prompts.py — can it be shorter and still pass all 8 categories
   (facts, math, sentiment, summarisation, NER, code debugging, logic, code generation)?
2. Whether max_tokens / temperature / model choice in agent/ can cut tokens without losing accuracy.
3. Robustness of the tasks.json parsing in agent/run.py against schema variants.
4. Any correctness risks in the 8 categories.

Propose concrete edits with before/after token impact. Don't over-engineer.
```

4. Bring whatever Codex suggests back to the group — we'll decide together what to keep.

> Note: Codex needs its own OpenAI API key (`export OPENAI_API_KEY=...`). If you don't have
> one, tell me and we'll find another reviewer.
