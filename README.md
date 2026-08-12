# NEO

A ReAct agent that reasons in a loop, calls tools when it needs facts, and answers
from what it found. Web search runs through a **self-hosted SearXNG** instance, so
searches don't go through a third-party API. Inference runs on Groq.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

---

## The loop

NEO implements ReAct: the model alternates between thinking and acting, and the
runner feeds tool results back as observations until an answer appears.

```
   Question
      │
      ▼
  ┌─────────┐   Action: <tool>: <arg>   ┌──────────────────┐
  │ Thought │ ───────────  PAUSE ─────▶ │ general_search   │ SearXNG (localhost)
  │         │                           │ wolfram_alpha    │ Wolfram Alpha API
  │         │ ◀────── Observation ───── └──────────────────┘
  └────┬────┘                                     ▲
       │  no answer yet ─────────────────────────┘
       │  (max 20 iterations)
       ▼
    Answer
```

The model never executes anything itself. It emits `Action: general_search: <query>`,
the runner matches that against a fixed dispatch table of exactly two functions, and
anything else comes back as `Observation: Tool not found`.

## Two ways to talk to it

```
>>> what's the capital of Nigeria?          → straight to the chat model, fast
>>> @think mass of Earth times 2            → full ReAct loop with tools
>>> @bye                                    → quit
```

Most messages don't need tools, and the loop costs several round trips, so `@think`
is opt-in rather than automatic.

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) — required
- A [Wolfram Alpha App ID](https://developer.wolframalpha.com/) — optional, only for
  the `wolfram_alpha` tool
- Docker, to run SearXNG — optional, only for the `general_search` tool

Without the optional two, plain chat still works and the tools report a failure
observation instead of crashing the loop.

## Setup

```bash
git clone https://github.com/krish-patel-01/NEO.git
cd NEO

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
cp .env.example .env             # then fill in GROQ_API_KEY
```

### SearXNG (for web search)

`general_search` expects a SearXNG instance on `http://127.0.0.1:8080` with the JSON
API enabled. The `searxng/` directory holds a working `settings.yml` and `uwsgi.ini`.

```bash
export SEARXNG_SECRET=$(openssl rand -hex 32)
./start_searxng.sh          # Linux/macOS
windows_xng.bat             # Windows — frees port 8080, then starts the container
```

Point elsewhere with `SEARXNG_HOST` if you already run one.

> `searxng/settings.yml` ships with `secret_key: "CHANGE_ME"`. Set `SEARXNG_SECRET`
> in the environment — it overrides the file — or edit it before exposing the
> instance to anything but localhost.

## Running

```bash
neo                                    # installed console script
python -m neo.chat                     # equivalent

python examples/run_query.py "28,800 seconds to hours"   # single query, no REPL
```

### HTTP API

An optional FastAPI wrapper exposes the same chat application over HTTP:

```bash
pip install -e ".[api]"
neo-api                                # or: uvicorn neo.api:app --port 9000
```

| Route | Method | Purpose |
|---|---|---|
| `/chat` | POST | `{"content": "...", "think_mode": false}` — `think_mode` routes through the agent |
| `/history` | GET | Full conversation history |
| `/clear_chat` | DELETE | Reset the history |

```bash
curl -X POST localhost:9000/chat \
  -H 'Content-Type: application/json' \
  -d '{"content": "mass of Earth times 2", "think_mode": true}'
```

> The API has **no authentication** and every caller shares one conversation
> history. It binds to `127.0.0.1` for that reason. Override with `NEO_API_HOST`
> only behind something that authenticates — anyone who can reach the port gets
> your Groq quota and the whole transcript.

## Configuration

All via environment variables, read from `.env`:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `GROQ_API_KEY` | yes | — | Groq authentication |
| `WOLFRAM_ALPHA_APPID` | no | — | Enables the `wolfram_alpha` tool |
| `NEO_MODEL` | no | `llama-3.3-70b-versatile` | Groq model ID |
| `SEARXNG_HOST` | no | `http://127.0.0.1:8080` | SearXNG instance |
| `SEARXNG_SECRET` | no | — | Overrides `secret_key` in `settings.yml` |

`NEO_MODEL` is configurable because Groq retires model IDs on a schedule — a
hardcoded one becomes a runtime 404 a few months later.

## Project layout

```
neo/
├── agent.py          # ReAct loop, Agent class, tool dispatch table
├── chat.py           # interactive console, @think routing
├── api.py            # optional FastAPI wrapper over chat.py
├── prompts.py        # ReAct system prompt
├── console.py        # coloured trace output
└── tools/
    ├── __init__.py   # general_search, wolfram_alpha — the callable surface
    ├── searxng.py    # SearXNG API wrapper
    └── wolfram.py    # Wolfram Alpha wrapper
examples/run_query.py # one-shot query
searxng/              # SearXNG config for the local instance
notebooks/            # original exploration, unmaintained
```

## Context handling

Groq enforces a tokens-per-minute limit, and a long ReAct trace hits it quickly. The
agent estimates token count (~6 chars/token) and, above 5000, drops the oldest two
exchanges while keeping the system prompt. On a `rate_limit_exceeded` error it
truncates and retries twice before giving up.

The estimate is deliberately crude — it only has to decide *when to trim*, so a real
tokenizer would cost more than it's worth here.

## Limitations

- **Tool results aren't verified.** Whatever SearXNG or Wolfram returns is fed back
  as fact; the model has no way to tell a wrong observation from a right one.
- **Answer parsing is string matching.** The runner splits on `"Answer:"`, so a model
  that writes the word mid-sentence terminates the loop early.
- **History truncation is blunt.** Dropping the oldest exchanges can discard context
  the current question depends on.
- **Search needs local infrastructure.** No SearXNG means no `general_search`.
- **Single user, single session.** History lives in memory and dies with the process.

## Security

`.env` is gitignored and must stay that way — it holds live API keys.

Tool calls go through a fixed dispatch dictionary in `neo/agent.py`. Earlier revisions
built a call string from model output and passed it to `eval()`, which let crafted
model output run arbitrary Python; the dispatch table can only reach the two declared
functions. Keep it that way when adding tools — register the function in `TOOLS`, don't
reintroduce dynamic evaluation.

## License

[MIT](LICENSE)
