# Build an AI Agent from Scratch — Workshop (DeepSeek Edition)

A 2-hour live-coding workshop: build a tool-calling ReAct agent from zero, in front of an
audience, on DeepSeek. This is the trimmed, DeepSeek-ported companion to the 10-chapter
[*Build an AI Agent from Scratch*](../ai-agent-from-scratch/README.md) book repo — same core
ideas, condensed to fit a single session.

## ⚠️ Before you present

- **`load_dotenv()` does not override variables already set in your shell.** If you (or your
  shell profile) ever `export`ed an API key manually, `.env` changes will be silently ignored
  and you'll auth with a stale key. `mini_agent`'s notebooks call
  `load_dotenv(override=True)` for exactly this reason — if you add your own `load_dotenv()`
  calls elsewhere, do the same, and if a key "isn't working" run
  `env | grep -i api_key` to check for a shadowing value before assuming the key is bad.
- We hit real, transient rate limits during testing on other providers' free tiers (a mid-demo
  429 can visibly stall a cell for 20–60s). `mini_agent/agent.py` retries transient errors
  (429/503/timeouts) with backoff so a demo won't hard-crash — expect an occasional pause,
  don't panic and re-run the cell. We have not hit rate limiting on DeepSeek in testing so far,
  but rehearse the full run-of-show at least once beforehand on the same key you'll present
  with, so any provider-side surprises show up before the room does.

## Setup

```bash
pip install -r requirements.txt
# or, if you use uv:
# uv pip install -r requirements.txt

cp .env.example .env
# edit .env: fill in DEEPSEEK_API_KEY (required), TAVILY_API_KEY (optional, for web_search)

jupyter lab
```

## What's here

- `mini_agent/agent.py` — the `Agent` class: a ReAct loop over `litellm.acompletion`
  (~130 lines, default model `deepseek/deepseek-chat`). `agent.messages` *is* the memory —
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
single ~130-line `Agent` class running on DeepSeek via [litellm](https://github.com/BerriAI/litellm).
The goal here is teachability in two hours, not feature completeness — everything fits on
screen and can be built live.
