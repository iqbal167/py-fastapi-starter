import os
from opentelemetry import trace

service_name = os.getenv("SERVICE_NAME", "fastapi-tracer")
tracer = trace.get_tracer(service_name)
