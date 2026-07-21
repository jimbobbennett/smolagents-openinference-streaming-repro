# smolagents + OpenInference: missing LLM spans when `stream_outputs=True`

Minimal reproducer for a gap in
[`openinference-instrumentation-smolagents`](https://pypi.org/project/openinference-instrumentation-smolagents/):
when a smolagents agent is built with **`stream_outputs=True`**, the resulting
trace contains `AGENT`, `CHAIN`, and `TOOL` spans but **no `LLM` spans**.

## Why

The instrumentor only wraps `Model.generate`. With `stream_outputs=True`,
smolagents calls `Model.generate_stream` instead, which the instrumentor never
patches — so no LLM span is ever created.

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in ARIZE_* and ANTHROPIC_API_KEY
set -a && source .env && set +a

# The bug: no LLM spans in the trace
STREAM=true python agent.py

# The expected behaviour: one LLM span per step
STREAM=false python agent.py
```

Open the Arize AX project afterwards and compare the two traces.

## Observed

| `stream_outputs` | Spans in the trace |
| --- | --- |
| `True` (default here) | `AGENT`, `CHAIN`, `TOOL` — **no `LLM`** |
| `False` | `AGENT`, `CHAIN`, `TOOL`, **`LLM`** (one per step) |

The same result can be verified offline with an in-memory span exporter — the
LLM span count is `0` when streaming and `>0` when not.

## Versions

- `smolagents` 1.25.0 / 1.26.0
- `openinference-instrumentation-smolagents` 0.1.31 / 0.1.32
- `arize-otel` 0.13.0

The behaviour is independent of the model provider (reproduces with both
`LiteLLMModel` for Anthropic and `OpenAIServerModel`).
