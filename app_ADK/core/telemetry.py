"""
OpenTelemetry setup — traces every LLM call, agent step, and Redis op.

If OTEL_ENABLED=false (default), this is a no-op so dev stays fast.
"""

import logging
from functools import wraps
from app_ADK.core.config import OTEL_ENABLED, OTEL_ENDPOINT, SERVICE_NAME

logger = logging.getLogger(__name__)

# ── Conditional OTEL setup ─────────────────────────────────────────────────────

if OTEL_ENABLED:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource

    resource = Resource(attributes={"service.name": SERVICE_NAME})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True))
    )
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(SERVICE_NAME)
    logger.info("OpenTelemetry enabled → %s", OTEL_ENDPOINT)

else:
    tracer = None
    logger.info("OpenTelemetry disabled (set OTEL_ENABLED=true to enable)")


# ── Span decorator ─────────────────────────────────────────────────────────────

def span(name: str):
    """
    Decorator that wraps an async function in an OTEL span.
    No-op if OTEL is disabled.

    Usage:
        @span("planner.create_plan")
        async def create_plan(...):
    """
    def decorator(fn):
        if not OTEL_ENABLED or tracer is None:
            return fn

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as s:
                try:
                    result = await fn(*args, **kwargs)
                    s.set_attribute("success", True)
                    return result
                except Exception as exc:
                    s.set_attribute("success", False)
                    s.set_attribute("error", str(exc))
                    s.record_exception(exc)
                    raise
        return wrapper
    return decorator


def get_trace_id() -> str:
    """Return current trace ID for logging correlation, or empty string."""
    if not OTEL_ENABLED or tracer is None:
        return ""
    from opentelemetry import trace as _trace
    ctx = _trace.get_current_span().get_span_context()
    if ctx and ctx.is_valid:
        return format(ctx.trace_id, "032x")
    return ""
