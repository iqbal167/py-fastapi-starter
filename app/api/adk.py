"""
Google ADK API endpoints for observability and health monitoring.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

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


@router.get("/logs")
async def query_logs(
    level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    hours_back: int = 1,
    settings: Settings = Depends(get_settings)
):
    """Query logs directly dari Loki."""
    with tracer.start_as_current_span("adk_query_logs_direct"):
        from app.core.observability_service import observability_service
        
        try:
            if search:
                result = await observability_service.query_logs(
                    query=search, limit=limit, hours_back=hours_back
                )
            else:
                result = await observability_service.query_logs(
                    level=level, limit=limit, hours_back=hours_back
                )
            return result
        except Exception as e:
            logger.error(f"Direct log query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces")
async def query_traces(
    service: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 20,
    hours_back: int = 1,
    settings: Settings = Depends(get_settings)
):
    """Query traces directly dari Jaeger."""
    with tracer.start_as_current_span("adk_query_traces_direct"):
        from app.core.observability_service import observability_service
        
        try:
            result = await observability_service.query_traces(
                service=service, operation=operation, limit=limit, hours_back=hours_back
            )
            return result
        except Exception as e:
            logger.error(f"Direct trace query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def analyze_performance(
    hours_back: int = 1,
    settings: Settings = Depends(get_settings)
):
    """Analyze system performance."""
    with tracer.start_as_current_span("adk_analyze_performance_direct"):
        from app.core.observability_service import observability_service
        
        try:
            result = await observability_service.analyze_performance(hours_back=hours_back)
            return result
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/observability-summary")
async def get_observability_summary(settings: Settings = Depends(get_settings)):
    """Get comprehensive observability summary."""
    with tracer.start_as_current_span("adk_observability_summary_direct"):
        from app.core.observability_service import observability_service
        
        try:
            # Get recent data
            recent_logs = await observability_service.query_logs(limit=5, hours_back=1)
            recent_traces = await observability_service.query_traces(limit=5, hours_back=1)
            metrics = await observability_service.get_metrics_summary()
            performance = await observability_service.analyze_performance(hours_back=1)
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "recent_logs_count": len(recent_logs.get('logs', [])),
                    "recent_traces_count": len(recent_traces.get('traces', [])),
                    "error_count": performance.get('analysis', {}).get('error_count', 0),
                    "avg_response_time_ms": performance.get('analysis', {}).get('avg_response_time_ms', 0),
                    "system_cpu_percent": metrics.get('system', {}).get('cpu_percent', 0),
                    "system_memory_percent": metrics.get('system', {}).get('memory', {}).get('percent', 0),
                    "issues_detected": len(performance.get('analysis', {}).get('issues', []))
                },
                "details": {
                    "logs": recent_logs,
                    "traces": recent_traces,
                    "metrics": metrics,
                    "performance": performance
                }
            }
        except Exception as e:
            logger.error(f"Observability summary failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-test-data")
async def generate_test_data(settings: Settings = Depends(get_settings)):
    """Generate test data untuk observability testing."""
    with tracer.start_as_current_span("adk_generate_test_data"):
        try:
            from app.core.test_data_generator import generate_test_data
            await generate_test_data()
            return {
                "status": "success",
                "message": "Test data generated successfully",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Test data generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/help")
def get_help():
    """Get help information about available ADK endpoints."""
    return {
        "endpoints": {
            "/adk/status": "Check if ADK agent is available and configured",
            "/adk/chat": "Chat with the observability agent for troubleshooting",
            "/adk/health-check": "Perform comprehensive health check",
            "/adk/metrics": "Get current system metrics",
            "/adk/logs": "Query logs directly dari Loki",
            "/adk/traces": "Query traces directly dari Jaeger",
            "/adk/performance": "Analyze system performance",
            "/adk/observability-summary": "Get comprehensive observability summary",
            "/adk/analyze": "Perform comprehensive system analysis",
            "/adk/help": "This help information"
        },
        "example_chat_messages": [
            "Tampilkan ringkasan observability sistem saat ini",
            "Ada error apa saja dalam 1 jam terakhir?",
            "Bagaimana performa sistem hari ini?",
            "Cek traces yang lambat",
            "Analisis logs untuk mencari masalah",
            "What is the current health status of the system?",
            "Are there any performance issues I should be aware of?",
            "Show me recent error logs",
            "Check slow traces and operations",
            "Analyze system performance trends"
        ],
        "observability_features": {
            "logs": "Query logs dari Loki dengan LogQL support",
            "traces": "Query distributed traces dari Jaeger",
            "metrics": "System dan application metrics",
            "performance": "Automated performance analysis",
            "chat": "Natural language interface untuk troubleshooting"
        },
        "configuration": {
            "required_env_vars": [
                "GEMINI_API_KEY (for Google ADK agent)"
            ],
            "optional_dependencies": [
                "psutil (for detailed system metrics)"
            ],
            "observability_stack": [
                "Loki (logs) - http://localhost:3100",
                "Jaeger (traces) - http://localhost:16686",
                "Grafana (visualization) - http://localhost:3000",
                "OTEL Collector - http://localhost:13133"
            ]
        }
    }