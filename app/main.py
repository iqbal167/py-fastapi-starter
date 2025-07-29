from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings, get_settings, Settings
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware
from app.core.tracer import setup_tracer
from app.core.instrumentation import instrument_fastapi_app
from app.core.telemetry.tracing import tracer

# Initialize tracing before creating FastAPI app
setup_tracer()

# Create FastAPI app with settings
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
    if not settings.is_production
    else None,
    docs_url=f"{settings.api_v1_prefix}/docs" if not settings.is_production else None,
    redoc_url=f"{settings.api_v1_prefix}/redoc" if not settings.is_production else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument the FastAPI app for automatic HTTP tracing
instrument_fastapi_app(app)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    with tracer.start_as_current_span("root"):
        return {
            "message": "Hello World",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    with tracer.start_as_current_span("health_check"):
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }


@app.get("/settings")
def get_app_settings(current_settings: Settings = Depends(get_settings)):
    """Get current application settings (non-sensitive data only)."""
    with tracer.start_as_current_span("get_settings"):
        return {
            "app_name": current_settings.app_name,
            "app_version": current_settings.app_version,
            "environment": current_settings.environment,
            "debug": current_settings.debug,
            "api_v1_prefix": current_settings.api_v1_prefix,
            "log_level": current_settings.log_level,
            "otel_service_name": current_settings.otel_service_name,
        }
