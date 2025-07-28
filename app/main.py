from fastapi import FastAPI
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware
from app.core.tracer import setup_tracer
from app.core.instrumentation import instrument_fastapi_app
from app.core.telemetry.tracing import tracer

# Initialize tracing before creating FastAPI app
setup_tracer()

app = FastAPI()

# Instrument the FastAPI app for automatic HTTP tracing
instrument_fastapi_app(app)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/")
def read_root():
    with tracer.start_as_current_span("root"):
        return {"message": "Hello World"}
