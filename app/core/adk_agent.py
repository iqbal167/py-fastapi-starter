"""
Google ADK Agent implementation for health check and observability.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Perbaikan import sesuai dokumentasi ADK
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from opentelemetry import trace
from app.core.settings import settings

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


async def health_check_function(component: str = "all") -> Dict[str, Any]:
    """Perform comprehensive health check on the FastAPI system.
    
    Args:
        component: Specific component to check (api, database, tracing, logging, all)
    
    Returns:
        Dictionary containing health check results
    """
    with tracer.start_as_current_span("adk_health_check"):
        try:
            if component == "all":
                result = await _check_all_components()
            elif component == "api":
                result = await _check_api_health()
            elif component == "database":
                result = await _check_database_health()
            elif component == "tracing":
                result = await _check_tracing_health()
            elif component == "logging":
                result = await _check_logging_health()
            else:
                result = {"error": f"Unknown component: {component}"}
            
            return result
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": f"Health check failed: {str(e)}"}

async def _check_all_components() -> Dict[str, Any]:
        """Check all system components."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check API
        api_result = await _check_api_health()
        results["components"]["api"] = api_result
        
        # Check database
        db_result = await _check_database_health()
        results["components"]["database"] = db_result
        
        # Check tracing
        tracing_result = await _check_tracing_health()
        results["components"]["tracing"] = tracing_result
        
        # Check logging
        logging_result = await _check_logging_health()
        results["components"]["logging"] = logging_result
        
        # Determine overall status
        unhealthy_components = [
            name for name, component in results["components"].items()
            if component.get("status") != "healthy"
        ]
        
        if unhealthy_components:
            results["overall_status"] = "degraded"
            results["unhealthy_components"] = unhealthy_components
        
        return results

async def _check_api_health() -> Dict[str, Any]:
        """Check API health."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:{settings.port}/health")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "error": "Non-200 status code"
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
async def _check_database_health() -> Dict[str, Any]:
        """Check database health."""
        # For SQLite, just check if file exists and is accessible
        try:
            import sqlite3
            import os
            
            if settings.database_url.startswith("sqlite"):
                db_path = settings.database_url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    # Try to connect and execute a simple query
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    conn.close()
                    return {"status": "healthy", "type": "sqlite"}
                else:
                    return {"status": "healthy", "type": "sqlite", "note": "Database file will be created on first use"}
            else:
                return {"status": "unknown", "note": "Non-SQLite database not implemented"}
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
async def _check_tracing_health() -> Dict[str, Any]:
        """Check OpenTelemetry tracing health."""
        try:
            # Check if OTEL collector is reachable
            import httpx
            otel_endpoint = settings.otel_exporter_otlp_endpoint.replace("4317", "13133")  # Health check port
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{otel_endpoint}")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "endpoint": settings.otel_exporter_otlp_endpoint,
                        "service_name": settings.otel_service_name
                    }
                else:
                    return {
                        "status": "degraded",
                        "endpoint": settings.otel_exporter_otlp_endpoint,
                        "note": "OTEL collector not reachable, traces may not be exported"
                    }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "note": "OTEL collector not reachable, traces may not be exported"
            }
async def _check_logging_health() -> Dict[str, Any]:
        """Check logging system health."""
        try:
            # Test if we can write to log
            test_logger = logging.getLogger("health_check_test")
            test_logger.info("Health check test log message")
            
            return {
                "status": "healthy",
                "log_level": settings.log_level,
                "handlers": len(logging.getLogger().handlers)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


async def system_metrics_function(metric_type: str = "all") -> Dict[str, Any]:
    """Get system metrics including CPU, memory, and application performance.
    
    Args:
        metric_type: Type of metrics to retrieve (system, application, all)
    
    Returns:
        Dictionary containing system metrics
    """
    with tracer.start_as_current_span("adk_system_metrics"):
        try:
            import psutil
            import os
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "metric_type": metric_type
            }
            
            if metric_type in ["system", "all"]:
                metrics["system"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory": {
                        "total": psutil.virtual_memory().total,
                        "available": psutil.virtual_memory().available,
                        "percent": psutil.virtual_memory().percent
                    },
                    "disk": {
                        "total": psutil.disk_usage('/').total,
                        "free": psutil.disk_usage('/').free,
                        "percent": psutil.disk_usage('/').percent
                    }
                }
            
            if metric_type in ["application", "all"]:
                process = psutil.Process(os.getpid())
                metrics["application"] = {
                    "pid": os.getpid(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_info": {
                        "rss": process.memory_info().rss,
                        "vms": process.memory_info().vms
                    },
                    "num_threads": process.num_threads(),
                    "create_time": process.create_time()
                }
            
            return metrics
        except ImportError:
            return {"error": "psutil not installed. Install with: pip install psutil"}
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {"error": f"Metrics collection failed: {str(e)}"}


async def query_logs_function(level: Optional[str] = None, limit: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
    """Query application logs with filters.
    
    Args:
        level: Log level to filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        limit: Maximum number of log entries to return
        search: Search term to filter logs
    
    Returns:
        Dictionary containing log query results
    """
    with tracer.start_as_current_span("adk_query_logs"):
        try:
            # This is a simplified implementation
            # In a real scenario, you'd query your log storage (Loki, etc.)
            query_params = {"level": level, "limit": limit, "search": search}
            logs = {
                "timestamp": datetime.now().isoformat(),
                "query_parameters": query_params,
                "logs": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Sample log entry for demonstration",
                        "service": settings.otel_service_name
                    }
                ],
                "note": "This is a simplified implementation. In production, integrate with your log storage system."
            }
            
            return logs
        except Exception as e:
            logger.error(f"Log query failed: {e}")
            return {"error": f"Log query failed: {str(e)}"}


class ObservabilityAgent:
    """Google ADK Agent for system observability and health monitoring."""
    
    def __init__(self, api_key: str):
        # Konfigurasi API key untuk Gemini
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Create function tools sesuai dengan format ADK terbaru
        health_check_tool = FunctionTool(
            func=health_check_function,
            description="Perform comprehensive health check on the FastAPI system"
        )
        
        system_metrics_tool = FunctionTool(
            func=system_metrics_function,
            description="Get system metrics including CPU, memory, and application performance"
        )
        
        query_logs_tool = FunctionTool(
            func=query_logs_function,
            description="Query application logs with filters"
        )
        
        self.tools = [health_check_tool, system_metrics_tool, query_logs_tool]
        
        # Create agent with tools sesuai dengan format ADK terbaru
        self.agent = Agent(
            name="FastAPI Observability Agent",
            model="gemini-1.5-flash",
            tools=self.tools,
            instruction="""You are an expert observability and monitoring agent for a FastAPI application.
            
            Your role is to:
            1. Monitor system health and performance
            2. Analyze logs and metrics
            3. Provide troubleshooting guidance
            4. Suggest optimizations
            5. Alert on potential issues
            
            You have access to tools that can:
            - Perform comprehensive health checks
            - Collect system and application metrics
            - Query application logs
            
            Always provide clear, actionable insights and recommendations.
            When issues are detected, suggest specific steps to resolve them.
            Use the available tools to gather current system state before making recommendations.
            
            Be concise but thorough in your responses.
            """
        )
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Chat with the observability agent."""
        with tracer.start_as_current_span("adk_agent_chat"):
            try:
                # Gunakan run_async method dari ADK terbaru
                response = await self.agent.run_async(message)
                return response
            except Exception as e:
                logger.error(f"ADK agent chat failed: {e}")
                return f"Sorry, I encountered an error: {str(e)}"
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        with tracer.start_as_current_span("adk_agent_health_check"):
            return await health_check_function("all")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        with tracer.start_as_current_span("adk_agent_metrics"):
            return await system_metrics_function("all")


def create_observability_agent(api_key: str) -> Optional[ObservabilityAgent]:
    """Create an observability agent instance."""
    if not api_key:
        logger.warning("Gemini API key not provided")
        return None
    
    try:
        return ObservabilityAgent(api_key)
    except Exception as e:
        logger.error(f"Failed to create observability agent: {e}")
        return None