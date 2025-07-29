from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from app.core.settings import settings


def setup_tracer():
    """Setup OpenTelemetry tracer with configuration from settings."""
    resource = Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.version": settings.otel_service_version,
            "deployment.environment": settings.environment,
        }
    )

    trace_provider = TracerProvider(resource=resource)

    # Use settings for OTLP endpoint
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(trace_provider)
    set_global_textmap(TraceContextTextMapPropagator())

    # Instrument HTTP client
    HTTPXClientInstrumentor().instrument()
