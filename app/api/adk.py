"""
Google ADK API endpoints for observability and health monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.core.settings import Settings, get_settings
from app.core.adk_agent import create_observability_agent, ObservabilityAgent
from app.core.telemetry.tracing import tracer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/adk", tags=["Google ADK"])


# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = None


class ChatResponse(BaseModel):
    response: str
    agent_available: bool


class HealthCheckResponse(BaseModel):
    timestamp: str
    overall_status: str
    components: Dict[str, Any]
    unhealthy_components: Optional[List[str]] = None


class SystemMetricsResponse(BaseModel):
    timestamp: str
    metric_type: str
    system: Optional[Dict[str, Any]] = None
    application: Optional[Dict[str, Any]] = None


# Global agent instance (will be initialized on first use)
_agent_instance: Optional[ObservabilityAgent] = None


def get_agent(settings: Settings = Depends(get_settings)) -> Optional[ObservabilityAgent]:
    """Get or create the ADK agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        api_key = settings.gemini_api_key
        if api_key:
            _agent_instance = create_observability_agent(api_key)
    
    return _agent_instance


@router.get("/status")
def adk_status(settings: Settings = Depends(get_settings)):
    """Check if Google ADK agent is available and configured."""
    with tracer.start_as_current_span("adk_status"):
        api_key = settings.gemini_api_key
        agent = get_agent(settings)
        
        return {
            "available": agent is not None,
            "api_key_configured": api_key is not None,
            "agent_name": "FastAPI Observability Agent" if agent else None,
            "model": "gemini-1.5-flash" if agent else None
        }


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    settings: Settings = Depends(get_settings)
):
    """Chat with the Google ADK observability agent."""
    with tracer.start_as_current_span("adk_chat"):
        agent = get_agent(settings)
        
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="ADK agent not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            # Convert Pydantic models to the format expected by the agent
            conversation_history = None
            if request.conversation_history:
                conversation_history = [
                    {
                        "role": msg.role,
                        "content": msg.content
                    }
                    for msg in request.conversation_history
                ]
            
            response = await agent.chat(request.message, conversation_history)
            
            return ChatResponse(
                response=response,
                agent_available=True
            )
        except Exception as e:
            logger.error(f"ADK chat failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error chatting with agent: {str(e)}"
            )


@router.get("/health-check", response_model=HealthCheckResponse)
async def perform_health_check(settings: Settings = Depends(get_settings)):
    """Perform comprehensive health check using ADK agent."""
    with tracer.start_as_current_span("adk_health_check"):
        agent = get_agent(settings)
        
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="ADK agent not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            result = await agent.perform_health_check()
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return HealthCheckResponse(**result)
        except Exception as e:
            logger.error(f"ADK health check failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}"
            )


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(settings: Settings = Depends(get_settings)):
    """Get system metrics using ADK agent."""
    with tracer.start_as_current_span("adk_metrics"):
        agent = get_agent(settings)
        
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="ADK agent not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            result = await agent.get_system_metrics()
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return SystemMetricsResponse(**result)
        except Exception as e:
            logger.error(f"ADK metrics collection failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Metrics collection failed: {str(e)}"
            )


@router.post("/analyze")
async def analyze_system(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    """Perform comprehensive system analysis using ADK agent."""
    with tracer.start_as_current_span("adk_analyze"):
        agent = get_agent(settings)
        
        if not agent:
            raise HTTPException(
                status_code=503,
                detail="ADK agent not available. Please check GEMINI_API_KEY configuration."
            )
        
        try:
            # Perform health check and metrics collection
            health_result = await agent.perform_health_check()
            metrics_result = await agent.get_system_metrics()
            
            # Create analysis prompt
            analysis_prompt = f"""
            Please analyze the current system state and provide insights:
            
            Health Check Results:
            {health_result}
            
            System Metrics:
            {metrics_result}
            
            Please provide:
            1. Overall system assessment
            2. Any issues or concerns identified
            3. Performance recommendations
            4. Suggested actions if any problems are found
            """
            
            analysis = await agent.chat(analysis_prompt)
            
            return {
                "analysis": analysis,
                "health_data": health_result,
                "metrics_data": metrics_result,
                "timestamp": health_result.get("timestamp")
            }
        except Exception as e:
            logger.error(f"ADK system analysis failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"System analysis failed: {str(e)}"
            )


@router.get("/help")
def get_help():
    """Get help information about available ADK endpoints."""
    return {
        "endpoints": {
            "/adk/status": "Check if ADK agent is available and configured",
            "/adk/chat": "Chat with the observability agent for troubleshooting",
            "/adk/health-check": "Perform comprehensive health check",
            "/adk/metrics": "Get current system metrics",
            "/adk/analyze": "Perform comprehensive system analysis",
            "/adk/help": "This help information"
        },
        "example_chat_messages": [
            "What is the current health status of the system?",
            "Are there any performance issues I should be aware of?",
            "How is the memory usage looking?",
            "Check if all services are running properly",
            "What are the current system metrics?",
            "Is the database connection healthy?",
            "Are there any errors in the logs?",
            "How can I improve system performance?"
        ],
        "configuration": {
            "required_env_vars": [
                "GOOGLE_ADK_API_KEY (or GEMINI_API_KEY as fallback)"
            ],
            "optional_dependencies": [
                "psutil (for detailed system metrics)"
            ]
        }
    }