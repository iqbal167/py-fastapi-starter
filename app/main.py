from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings, get_settings, Settings
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware
from app.core.tracer import setup_tracer
from app.core.instrumentation import instrument_fastapi_app
from app.core.telemetry.tracing import tracer
from app.core.logger import get_logger

# Initialize tracing
setup_tracer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger = get_logger("app.startup")
    logger.info(
        "Application starting up",
        event_type="app_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    
    yield
    
    # Shutdown
    logger = get_logger("app.shutdown")
    logger.info("Application shutting down", event_type="app_shutdown")


# Create FastAPI app with lifespan and settings
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
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

# Add custom middleware (order matters - RequestID should be first)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/")
def read_root():
    """Root endpoint that returns a welcome message."""
    logger = get_logger("app.endpoint")
    
    with tracer.start_as_current_span("root"):
        response_data = {
            "message": "Hello World",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }
        
        # Simple business logic logging - event_type from middleware
        logger.info("Application info requested", 
                   app_name=settings.app_name,
                   version=settings.app_version)
        
        return response_data


@app.get("/health")
def health_check():
    """Health check endpoint."""
    with tracer.start_as_current_span("health_check"):
        response_data = {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }
        return response_data


@app.get("/settings")
def get_app_settings(current_settings: Settings = Depends(get_settings)):
    """Get current application settings (non-sensitive data only)."""
    logger = get_logger("app.endpoint")
    
    with tracer.start_as_current_span("get_settings"):
        response_data = {
            "app_name": current_settings.app_name,
            "app_version": current_settings.app_version,
            "environment": current_settings.environment,
            "debug": current_settings.debug,
            "api_v1_prefix": current_settings.api_v1_prefix,
            "log_level": current_settings.log_level,
            "otel_service_name": current_settings.otel_service_name,
        }
        
        # Simple business logic logging - event_type from middleware
        logger.info("Settings retrieved",
                   environment=current_settings.environment,
                   debug=current_settings.debug)
        
        return response_data

