# 🏁 Team Handover — AMD Hackathon Act II (Track 1)

**Read this first.** One page, plain English. It explains what we're building, where it
stands, and what each of us needs to do before the deadline.

> ⏰ **Deadline: 6 PM CET, 11 July 2026.**

---

## 1. TL;DR (30 seconds)

- We entered **Track 1**: build an AI agent that answers 8 kinds of tasks as **cheaply** as possible.
- Our agent is **built, tested, and submitted.** It's live and working.
- What's left is **tuning it to score higher**, and a **second-opinion review**.
- Our submission (a Docker image URL): `ghcr.io/talvin29/amd-track1:latest`
- Our code: <https://github.com/TALVIN29/AMD>

---

## 2. Important links

| What | Where |
|------|-------|
| Our code (GitHub) | https://github.com/TALVIN29/AMD |
| Our submission image | `ghcr.io/talvin29/amd-track1:latest` |
| Hackathon page | https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii |
| Track 1 leaderboard | https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii/live?track=1#amd-leaderboard |
| GPU / compute access | https://notebooks.amd.com/hackathon |
| Discord (ask questions) | LabLab.ai Discord → AMD Hackathon Act-2 |

---

## 3. What Track 1 actually is (and how we win)

The judges give our agent a bunch of tasks across **8 categories**: factual Q&A, math,
sentiment, summarising, finding names in text (NER), code debugging, logic puzzles, and
writing code.

Scoring has **two steps**:
1. **Accuracy gate** — are our answers correct? If not enough are right, we're out.
2. **Token efficiency** — of everyone who passes, whoever spent the **fewest tokens** on the
   paid **Fireworks AI** wins. (A "token" ≈ a word-piece; the paid AI charges by tokens.)

**The key trick:** a **local** AI model that runs *inside our own program* is **FREE** — its
tokens don't count against us. The organizers literally say: *run as many local models as you
need; call the paid Fireworks AI as little as possible.*

So our agent is a **smart router**:

```
each task ─▶ is it easy? ─▶ answer with our FREE local model      (0 tokens)
          └▶ is it hard? ─▶ send to paid Fireworks AI             (costs tokens)
```

- **Easy** (facts, sentiment, names, summaries) → answered locally, **free**.
- **Hard** (math, logic, code) → sent to Fireworks, because a small local model would get
  them wrong and fail the accuracy gate.

The more we can safely move to "local," the fewer tokens we spend, the higher we rank.

---

## 4. Current status — what's done

✅ Agent built as a proper one-shot program (reads tasks → answers → writes results → stops).
✅ Bundled a small local AI model (runs on the judges' modest hardware: 4 GB RAM, 2 CPUs, no GPU).
✅ Smart routing: easy→local (free), hard→Fireworks.
✅ Packaged as a Docker image, made public, **submitted**.
✅ Tested end-to-end: correct answers (e.g. "Paris", "96", "Positive"), valid output, no crashes.

🔲 **Tune it** to move more tasks to "local" without losing accuracy (higher rank).
🔲 **Codex review** — a second pair of eyes (see §7, this is a job for one of us).
🔲 **Confirm the exact task file format** with organizers on Discord.

**Honest note:** the first version I built sent *everything* to Fireworks, because an older
copy of the rules implied that was required. The updated rules flipped it (local is free) —
so it was rebuilt as the smart router above. The old version still works as a backup; the
new one is what's submitted.

---

## 5. What's in the repo (plain English)

| File / folder | What it is |
|---------------|-----------|
| `agent/run.py` | The main program: reads the tasks, answers them, writes results. |
| `agent/router.py` | The decision: answer locally (free) or send to Fireworks. |
| `agent/local.py` | Runs our free local AI model. |
| `agent/fireworks.py` | Calls the paid Fireworks AI (only for hard tasks). |
| `agent/prompts.py` | The short instructions we give the AI (short = fewer tokens). |
| `eval/` | Practice questions + a script to measure our accuracy and token use. |
| `Dockerfile` | The recipe that packages everything into the submission image. |
| `README.md` | The technical version of this document. |
| `docs/SETUP.md` | Step-by-step: make the accounts, build & publish the image. |
| `docs/TEAM_BRIEF.md` | The Codex-review task (also in §7 below). |

---

## 6. How to build, test, and (re)submit

Full click-by-click steps are in **`docs/SETUP.md`**. Short version:

**Accounts needed:** Fireworks AI (for testing) + GitHub (we already have it, for hosting the image).

**To rebuild and re-submit after any change:**
```bash
# 1. build the image
docker build --platform linux/amd64 -t ghcr.io/talvin29/amd-track1:latest .
# 2. publish it (after `docker login ghcr.io -u TALVIN29 -p <token>` once)
docker push ghcr.io/talvin29/amd-track1:latest
# 3. re-submit the URL on lablab:  ghcr.io/talvin29/amd-track1:latest
```
We can re-submit up to **10 times per hour**, so test first, then submit improvements.

**To test locally without submitting** (checks it doesn't crash):
```bash
docker run --rm -e AGENT_DRY_RUN=1 -v "$PWD/eval:/input:ro" -v "$PWD/out:/output" \
  ghcr.io/talvin29/amd-track1:latest
# (put a tasks.json in the eval folder first — eval/sample_tasks.json is an example)
```

---

## 7. 🙋 Who does what (before 11 July)

Let's split it. Suggested:

**Person A — Codex review (second opinion on the code).**
1. Install: `npm install -g @openai/codex`
2. In the repo folder, run: `codex`
3. Paste the review prompt from **`docs/TEAM_BRIEF.md`** (§"Your task").
4. Bring the suggestions to the group; we decide what to keep.
   *(Codex needs an OpenAI API key. No key? Tell the group.)*

**Person B — Tuning (this is where the score improves).**
1. Get the Fireworks key working (`docs/SETUP.md` §1) on the AMD GPU box (https://notebooks.amd.com/hackathon).
2. Run `python -m eval.harness` and read the summary: accuracy, how many answered locally, total tokens.
3. Try moving more categories to "local"; try a smaller/faster or different local model.
4. Goal: **highest share of local answers that still passes accuracy.**

**Person C — Coordination + submissions.**
1. Ask on Discord for the **exact `tasks.json` format** (field names) if they'll share it.
2. Keep an eye on the **leaderboard**; re-submit improved images.
3. Watch the **deadline** and make sure a valid image is always submitted.

*(Swap these around however suits us — the point is all three get covered.)*

---

## 8. Mini-glossary

- **Token** — a word-piece; the paid AI bills by tokens. Fewer = we rank higher.
- **Local model** — an AI that runs inside our own program; **free** (doesn't count as tokens).
- **Fireworks AI** — the paid AI service; the thing we're trying to use as little as possible.
- **Docker image** — our whole program packed into one shippable box; the submission is a link to it.
- **GGUF / quantized** — a compressed, shrunk-down AI model small enough to run on a plain CPU.
- **Accuracy gate** — the minimum correctness bar; below it, we don't get ranked at all.

---

Questions about any of this → ping the group, or drop it in the hackathon Discord.
