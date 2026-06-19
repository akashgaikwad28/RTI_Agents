"""
observability/trace_exporter.py
--------------------------------
OpenTelemetry stubs for future Jaeger, Grafana Tempo, or Datadog integrations.
Currently provides a no-op / basic interface to be implemented later.
"""

from observability.logger import get_logger
from config.settings import settings

logger = get_logger("trace_exporter")

def setup_opentelemetry():
    """
    Initializes OpenTelemetry TracerProvider, SpanProcessors, and Exporters.
    To be activated when OTEL is deployed.
    """
    if not getattr(settings, "ENABLE_OPENTELEMETRY", False):
        logger.info(
            "OpenTelemetry export disabled.",
            extra={"event": "otel_disabled", "component": "api", "operation": "startup"}
        )
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": "rti-agent", "environment": settings.APP_ENV})
        provider = TracerProvider(resource=resource)
        
        # Configure Jaeger / Datadog exporter endpoint here later
        otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
        processor = BatchSpanProcessor(otlp_exporter)
        
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
        logger.info(
            "OpenTelemetry configured successfully.",
            extra={"event": "otel_enabled", "component": "api", "operation": "startup"}
        )
    except ImportError:
        logger.warning(
            "opentelemetry SDK not installed. Skipping OTEL setup.",
            extra={"event": "otel_missing", "component": "api", "operation": "startup"}
        )

def get_tracer(name: str):
    """Returns a tracer instance."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        # Fallback dummy tracer
        class DummyTracer:
            def start_as_current_span(self, *args, **kwargs):
                import contextlib
                @contextlib.contextmanager
                def dummy_span():
                    yield None
                return dummy_span()
        return DummyTracer()
