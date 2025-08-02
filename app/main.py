from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.settings import settings, get_settings, Settings
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware
from app.core.tracer import setup_tracer
from app.core.instrumentation import instrument_fastapi_app
from app.core.telemetry.tracing import tracer
from app.core.gemini import get_gemini_service

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


# Pydantic models for Gemini endpoints
class GenerateTextRequest(BaseModel):
    prompt: str
    temperature: float = 0.7


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@app.post("/api/v1/gemini/generate")
async def generate_text(request: GenerateTextRequest, current_settings: Settings = Depends(get_settings)):
    """Generate text using Google Gemini AI."""
    with tracer.start_as_current_span("gemini_generate_text"):
        from app.core.gemini import create_gemini_service
        gemini = create_gemini_service(current_settings.gemini_api_key)
        if not gemini:
            raise HTTPException(
                status_code=503, 
                detail="Gemini service not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            response = await gemini.generate_text(request.prompt)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


@app.post("/api/v1/gemini/chat")
async def chat_with_gemini(request: ChatRequest, current_settings: Settings = Depends(get_settings)):
    """Chat with Google Gemini AI."""
    with tracer.start_as_current_span("gemini_chat"):
        from app.core.gemini import create_gemini_service
        gemini = create_gemini_service(current_settings.gemini_api_key)
        if not gemini:
            raise HTTPException(
                status_code=503,
                detail="Gemini service not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            # Convert Pydantic models to dict format expected by the service
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            response = await gemini.chat(messages)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


@app.get("/api/v1/gemini/status")
def gemini_status(current_settings: Settings = Depends(get_settings)):
    """Check if Gemini service is available."""
    with tracer.start_as_current_span("gemini_status"):
        from app.core.gemini import create_gemini_service
        gemini = create_gemini_service(current_settings.gemini_api_key)
        return {
            "available": gemini is not None,
            "model": gemini.config.model_name if gemini else None,
            "api_key_configured": current_settings.gemini_api_key is not None
        }
