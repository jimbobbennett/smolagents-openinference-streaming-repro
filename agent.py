"""Minimal smolagents agent that reproduces missing LLM spans under streaming.

The OpenInference smolagents instrumentor only wraps ``Model.generate``. When a
``ToolCallingAgent`` (or ``CodeAgent``) is built with ``stream_outputs=True``,
smolagents calls ``Model.generate_stream`` instead, which the instrumentor never
sees — so the trace has AGENT / CHAIN / TOOL spans but **no LLM spans**.

Usage:
    STREAM=true  python agent.py   # reproduces the bug: no LLM spans (default)
    STREAM=false python agent.py   # working case: one LLM span per step
"""

import os

# Initialise tracing before constructing any smolagents model so the
# instrumentor patches the model classes first.
from tracing import PROJECT_NAME, init_tracing

tracer_provider = init_tracing()

from smolagents import LiteLLMModel, ToolCallingAgent, tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to look up the weather for.
    """
    return f"It is sunny and 22 degrees C in {city}."


def _stream_enabled() -> bool:
    return os.environ.get("STREAM", "true").strip().lower() not in ("false", "0", "no")


def main() -> None:
    stream = _stream_enabled()

    model = LiteLLMModel(model_id=os.environ.get("MODEL_ID", "anthropic/claude-sonnet-4-6"))
    agent = ToolCallingAgent(
        tools=[get_weather],
        model=model,
        # stream_outputs=True routes the model call through generate_stream,
        # which the OpenInference instrumentor does not wrap -> no LLM spans.
        stream_outputs=stream,
    )

    print(f"Running agent with stream_outputs={stream} ...\n")
    result = agent.run("What is the weather in London?")
    print("\nAgent result:", result)

    # Trace processors don't always flush before the process exits.
    tracer_provider.force_flush()
    print(
        f"\nDone. Open the Arize AX project '{PROJECT_NAME}' to inspect the trace.\n"
        "  stream_outputs=True  -> AGENT / CHAIN / TOOL spans, but NO LLM spans (the bug)\n"
        "  stream_outputs=False -> one LLM span per step (expected)"
    )


if __name__ == "__main__":
    main()
