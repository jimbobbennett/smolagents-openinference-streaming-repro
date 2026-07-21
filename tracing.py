"""Arize AX tracing setup for the smolagents reproducer.

Registers an OTel tracer provider pointed at Arize AX and installs the
OpenInference smolagents instrumentor. Call ``init_tracing()`` *before*
importing/constructing any smolagents model so the instrumentor can patch the
model classes first.
"""

import os

from arize.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

PROJECT_NAME = os.environ.get("ARIZE_PROJECT_NAME", "smolagents-streaming-repro")


def init_tracing():
    tracer_provider = register(
        space_id=os.environ["ARIZE_SPACE_ID"],
        api_key=os.environ["ARIZE_API_KEY"],
        project_name=PROJECT_NAME,
    )
    SmolagentsInstrumentor().instrument(tracer_provider=tracer_provider)
    return tracer_provider
