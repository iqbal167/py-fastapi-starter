"""
Google ADK Agent implementation for health check and observability.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Menggunakan Gemini langsung karena ADK belum tersedia
import google.generativeai as genai
from opentelemetry import trace
from app.core.settings import settings
from app.core.observability_service import observability_service

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


async def query_logs_function(level: Optional[str] = None, limit: int = 10, search: Optional[str] = None, hours_back: int = 1) -> Dict[str, Any]:
    """Query application logs with filters dari Loki.
    
    Args:
        level: Log level to filter (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        limit: Maximum number of log entries to return
        search: Search term to filter logs
        hours_back: Hours back to search
    
    Returns:
        Dictionary containing log query results
    """
    with tracer.start_as_current_span("adk_query_logs"):
        try:
            if search:
                result = await observability_service.query_logs(query=search, limit=limit, hours_back=hours_back)
            else:
                result = await observability_service.query_logs(level=level, limit=limit, hours_back=hours_back)
            
            return result
        except Exception as e:
            logger.error(f"Log query failed: {e}")
            return {"error": f"Log query failed: {str(e)}"}


async def query_traces_function(service: Optional[str] = None, operation: Optional[str] = None, 
                               limit: int = 20, hours_back: int = 1) -> Dict[str, Any]:
    """Query distributed traces dari Jaeger.
    
    Args:
        service: Service name to filter
        operation: Operation name to filter
        limit: Maximum number of traces to return
        hours_back: Hours back to search
    
    Returns:
        Dictionary containing trace query results
    """
    with tracer.start_as_current_span("adk_query_traces"):
        try:
            result = await observability_service.query_traces(
                service=service, operation=operation, limit=limit, hours_back=hours_back
            )
            return result
        except Exception as e:
            logger.error(f"Trace query failed: {e}")
            return {"error": f"Trace query failed: {str(e)}"}


async def analyze_performance_function(hours_back: int = 1) -> Dict[str, Any]:
    """Analisis performa sistem berdasarkan logs, traces, dan metrics.
    
    Args:
        hours_back: Hours back to analyze
    
    Returns:
        Dictionary containing performance analysis
    """
    with tracer.start_as_current_span("adk_analyze_performance"):
        try:
            result = await observability_service.analyze_performance(hours_back=hours_back)
            return result
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {"error": f"Performance analysis failed: {str(e)}"}


async def get_observability_summary_function() -> Dict[str, Any]:
    """Dapatkan ringkasan lengkap observability data.
    
    Returns:
        Dictionary containing comprehensive observability summary
    """
    with tracer.start_as_current_span("adk_observability_summary"):
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
            return {"error": f"Observability summary failed: {str(e)}"}


class ObservabilityAgent:
    """Observability Agent menggunakan Gemini untuk system monitoring."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.system_prompt = """You are an expert observability and monitoring agent for a FastAPI application with complete observability stack (Logs, Traces, Metrics).
        
        Your role is to:
        1. Monitor system health and performance in real-time
        2. Analyze logs dari Loki dengan LogQL queries
        3. Investigate distributed traces dari Jaeger
        4. Collect dan analyze system/application metrics
        5. Provide troubleshooting guidance berdasarkan observability data
        6. Suggest optimizations dan performance improvements
        7. Alert on potential issues dan anomalies
        
        When user asks about observability data, you should gather current system information and provide actionable insights.
        
        Respond in Indonesian when user asks in Indonesian, English when user asks in English.
        Be concise but thorough in your responses.
        """
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Chat with the observability agent."""
        with tracer.start_as_current_span("adk_agent_chat"):
            try:
                # Gather observability data berdasarkan pertanyaan
                context_data = await self._gather_context_data(message)
                
                # Build prompt dengan context
                full_prompt = f"{self.system_prompt}\n\nCurrent System Data:\n{context_data}\n\nUser Question: {message}\n\nPlease provide a helpful response based on the current system data."
                
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"Agent chat failed: {e}")
                return f"Sorry, I encountered an error: {str(e)}"
    
    async def _gather_context_data(self, message: str) -> str:
        """Gather relevant observability data berdasarkan user message."""
        context = []
        
        try:
            # Always get basic health and metrics
            health_data = await health_check_function()
            metrics_data = await system_metrics_function()
            
            context.append(f"Health Status: {health_data}")
            context.append(f"System Metrics: {metrics_data}")
            
            # Get specific data berdasarkan keywords
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['log', 'error', 'warning']):
                logs_data = await query_logs_function(limit=5)
                context.append(f"Recent Logs: {logs_data}")
            
            if any(word in message_lower for word in ['trace', 'slow', 'performance']):
                traces_data = await query_traces_function(limit=5)
                performance_data = await analyze_performance_function()
                context.append(f"Recent Traces: {traces_data}")
                context.append(f"Performance Analysis: {performance_data}")
            
            if any(word in message_lower for word in ['summary', 'overview', 'ringkasan']):
                summary_data = await get_observability_summary_function()
                context.append(f"Observability Summary: {summary_data}")
                
        except Exception as e:
            context.append(f"Error gathering context: {str(e)}")
        
        return "\n".join(context)
    
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