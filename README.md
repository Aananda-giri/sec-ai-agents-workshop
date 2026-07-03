# Build an AI Agent from Scratch — Workshop (Gemini Edition)

A 2-hour live-coding workshop: build a tool-calling ReAct agent from zero, in front of an
audience, on Gemini. This is the trimmed, Gemini-ported companion to the 10-chapter
[*Build an AI Agent from Scratch*](../ai-agent-from-scratch/README.md) book repo — same core
ideas, condensed to fit a single session.

## ⚠️ Before you present: rate limits — read this, it will bite you

The Gemini free tier throttles `gemini-2.5-flash` on **two** axes at once, and one of them is
a **hard daily cap**, not just a per-minute one:

- As low as **5 requests/minute**, *and*
- On the key we tested with, **`GenerateRequestsPerDayPerProjectPerModel-FreeTier` = 20
  requests per day, total, for that one model.**

We hit both live: a 429 with `retryDelay: 44s` (per-minute), and later a 429 whose quota
metadata explicitly said `"quotaValue": "20"` per day — at which point `mini_agent/agent.py`'s
retry-with-backoff (built for the per-minute case) just spins uselessly, because no amount of
waiting resets a daily quota. **A single rehearsal run-through can burn most or all of a
free-tier key's daily budget before you ever get in front of the room.**

Do this beforehand — not optional for a live 2-hour session:

1. **Enable billing on your Gemini API project before presenting.** It costs cents for a whole
   workshop's worth of calls and lifts both the per-minute and per-day free-tier ceilings.
   See [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and
   [pricing](https://ai.google.dev/gemini-api/docs/pricing).
2. **Rehearse on a billed key**, or budget your free-tier rehearsal calls carefully — don't
   `evaluate()` the full `SAMPLE_GAIA` set more than once a day on a free key.
3. **Fallback model**: if `gemini-2.5-flash` is still capped on the day, try
   `gemini/gemini-2.0-flash-lite` or `gemini/gemini-2.5-flash-lite` — untested by us, but as a
   *different model* it likely has its own separate daily quota bucket, worth trying live if
   you get capped mid-session.
4. `mini_agent/agent.py` retries transient errors (429/503/timeouts) with backoff, which
   handles per-minute throttling gracefully (expect occasional 20–60s pauses — don't panic and
   re-run the cell). It cannot do anything about a daily cap; that needs billing enabled ahead
   of time.

## Setup

```bash
pip install -r requirements.txt
# or, if you use uv:
# uv pip install -r requirements.txt

cp .env.example .env
# edit .env: fill in GEMINI_API_KEY (required), TAVILY_API_KEY (optional, for web_search)

jupyter lab
```

## What's here

- `mini_agent/agent.py` — the `Agent` class: a ReAct loop over `litellm.acompletion`
  (~130 lines, default model `gemini/gemini-2.5-flash`). `agent.messages` *is* the memory —
  there's no separate memory system in this workshop.
- `mini_agent/tools.py` — `calculator`, `web_search` (Tavily-backed, degrades gracefully
  without a key), `execute_python` (local subprocess, no sandbox), and `write_tool` /
  `load_generated_tools` — the self-extension finale where the agent writes its own tool.
- `mini_agent/gaia.py` — `SAMPLE_GAIA` (4 bundled offline GAIA-style questions, no HF token
  needed), the `evaluate()` scoring harness, and optional `load_hf_gaia()` for the real gated
  HF dataset if you have `datasets` + `HF_TOKEN` set up.
- `notebooks/01_simplest_agent.ipynb` … `05_evaluation_gaia.ipynb` — the live-coding notebooks.

## Run of show

~120 minutes total. These are guide rails — adjust live based on room energy and questions.

| Segment | Format | Notebook | Time |
|---|---|---|---|
| Introduction to Agents | Talk | — | 8 min |
| Act 1 — the simplest possible agent | Live code | `01_simplest_agent.ipynb` | 12 min |
| Act 2 — tools + the ReAct loop | Live code | `02_tools_and_react.ipynb` | 20 min |
| Act 3 — memory + code execution | Live code | `03_memory_and_code_execution.ipynb` | 20 min |
| Act 4 — self-extending agent (finale) | Live code | `04_self_extending_agent.ipynb` | 15 min |
| Act 5 — evaluation on GAIA | Live code | `05_evaluation_gaia.ipynb` | 15 min |
| Frameworks, coding agents, real-world use | Talk/discussion | — | 10 min |
| Q&A | Discussion | — | 20 min |

The "frameworks" segment is where Claude Code, Cursor, LangGraph, CrewAI, MCP, and
multi-agent patterns get mentioned — and where the cut book chapters (below) resurface
conceptually rather than in code.

## What we cut and why

To fit 2 hours, this workshop skips everything the book covers beyond a basic ReAct loop:
RAG, long-term/vector memory, planning and reflection, multi-agent orchestration (A2A),
MCP, and skills discovery. These are all discussion-only talking points here, not live code.
For the full treatment, see the chapter table in
[`../ai-agent-from-scratch/README.md`](../ai-agent-from-scratch/README.md).

## How this differs from the book

Same ReAct-loop ideas (think → act → observe, tools as plain functions, messages as memory),
ported from the book's OpenAI/Anthropic-based, multi-module `scratch_agents` framework to a
single ~130-line `Agent` class running on Gemini via [litellm](https://github.com/BerriAI/litellm).
The goal here is teachability in two hours, not feature completeness — everything fits on
screen and can be built live.
