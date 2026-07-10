# Slide Deck Brief — what to build, in plain English

For whoever builds the slides (Canva, Google Slides, PowerPoint — any tool is fine) or whoever
runs Codex/an AI tool to auto-generate a deck. Content below is real project detail; fill the
`[TODO]` spots with real numbers once someone runs `eval/harness.py` with a Fireworks key
(see `docs/SETUP.md`) — don't invent numbers for these.

Target: **8-9 slides**, simple, one main idea per slide. lablab's submission needs a Slide
Presentation file — this covers it.

---

## Slide-by-slide content

**1. Title**
- Project name: Smart-Router Agent (or your team's project title)
- Tagline: "Answers every Track 1 task category — spends as few paid AI tokens as possible."
- Team names, AMD Developer Hackathon Act II, Track 1: General-Purpose AI Agent
- *Presenter note:* one sentence — "We built an AI agent that's graded on being correct first, cheap second."

**2. The challenge**
- Track 1: agent must handle 8 task types — factual Q&A, math, sentiment, summarisation,
  named entity recognition, code debugging, logic puzzles, code generation.
- Scoring is two-step: (1) pass an 80% accuracy bar over 19 fixed tasks, (2) among those who
  pass, rank by fewest tokens spent on the paid Fireworks AI.
- *Presenter note:* "Being right isn't enough — you also have to be cheap. But cheap only counts if you already passed the accuracy bar."

**3. The key insight**
- A small AI model can run *inside our own program*, for free — its answers count toward
  accuracy, but its cost is zero (confirmed directly by the organizers).
- So: answer easy tasks with our own free small model. Only pay for the tasks that actually need
  a bigger, paid AI.
- *Presenter note:* "The trick isn't a smarter AI — it's knowing when you don't need one."

**4. How it works (architecture)**
- Diagram (simple boxes-and-arrows, recreate visually):
  ```
  incoming task → is it math / logic / code?
                     │yes                    │no
                     ▼                        ▼
              paid AI (Fireworks)       our own free small AI
              (picks the model best     (runs on the judge's own
               suited: a code model      hardware, zero cost)
               for code tasks, a
               general model otherwise)
                     │
                     └── if the paid AI call fails → falls back
                         to our free model, so no task is ever skipped
  ```
- *Presenter note:* "Every task gets an answer, no matter what — and most of them cost nothing."

**5. What we built it with**
- One-shot Docker container: reads the task list, answers each one, writes results, exits —
  no server, no waiting.
- Free local model: a small (2-3 billion parameter) compressed AI model, small enough to run on
  the judge's plain CPU box (no GPU) in the 4GB memory limit.
- Paid path only touches Fireworks AI's official models — never our own key, never a bypass.
- *Presenter note:* "It has to run on a judge's plain laptop-grade machine — no GPU, 4GB of memory. Everything is sized for that."

**6. A real risk we caught and fixed**
- The official example task format doesn't actually label *what kind* of task it is (no "this
  is math" tag). Our router needed that label to know when to spend money.
- Fix: taught the program to guess the task type from its wording when no label is given — a
  cheap backup, not a rebuild, and it never costs anything extra when a label *is* present.
- *Presenter note:* "We didn't just build it — we stress-tested our own assumptions against what the organizers actually published, and caught a gap before it could've cost us the accuracy bar."

**7. Results**
- Accuracy: `[TODO: fill in from eval/harness.py output, e.g. "17/19 (89%) on practice tasks"]`
- Tokens spent: `[TODO: fill in total Fireworks tokens from harness run]`
- Local vs. paid split: `[TODO: e.g. "14 of 19 tasks answered for free"]`
- Docker image size: 4.15GB (comfortably under the 10GB limit)
- *Presenter note:* "The fewer tasks that need the paid AI, the higher we rank — as long as we stay above the accuracy bar."

**8. Demo**
- Screenshot or short screen-recording of the container running: input tasks in, `results.json`
  out, showing the per-task routing log (which tasks went free vs. paid).
- *Presenter note:* keep this under 30 seconds of screen time — show it running, don't narrate every line.

**9. Team & links**
- Team member names + who did what (build / tuning / coordination)
- GitHub: github.com/TALVIN29/AMD
- Submission image: ghcr.io/talvin29/amd-track1:latest
- *Presenter note:* thank the judges, invite questions.

---

## Codex prompt (if generating the deck with an AI tool)

Paste this into Codex (or any coding-capable AI) after filling in the `[TODO]` numbers above:

```
Build a simple slide deck as a Marp markdown file (deck.md) that renders to PDF/PPTX.
8-9 slides, one idea per slide, minimal text, no more than 4-5 bullet points per slide.
Use this content and structure exactly as given (do not invent numbers or facts):

[paste the "Slide-by-slide content" section above, with TODOs filled in]

Style: clean, technical-but-approachable, dark or light theme is fine. Include a simple
architecture diagram on slide 4 (ASCII-to-visual is fine, or a basic shapes diagram).
After generating deck.md, tell me the exact command to convert it to PDF using the marp-cli
(e.g. npx @marp-team/marp-cli deck.md --pdf).
```
