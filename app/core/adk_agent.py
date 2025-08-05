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
            # Fix: Use correct port 13133 instead of 113133
            otel_health_endpoint = "http://localhost:13133"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(otel_health_endpoint)
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "endpoint": settings.otel_exporter_otlp_endpoint,
                        "health_endpoint": otel_health_endpoint,
                        "service_name": settings.otel_service_name
                    }
                else:
                    return {
                        "status": "degraded",
                        "endpoint": settings.otel_exporter_otlp_endpoint,
                        "health_endpoint": otel_health_endpoint,
                        "note": "OTEL collector not reachable, traces may not be exported"
                    }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "endpoint": settings.otel_exporter_otlp_endpoint,
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
        
        self.system_prompt = """You are an expert observability and monitoring agent for a FastAPI application.
        
        IMPORTANT INSTRUCTIONS:
        1. Always analyze the provided system data carefully
        2. Give specific, actionable insights based on actual data
        3. Highlight any issues or anomalies found
        4. Provide clear recommendations
        5. Use emojis and formatting for better readability
        6. Respond in the same language as the user's question
        
        When analyzing data:
        - Focus on ERROR and WARNING logs first
        - Check response times and performance metrics
        - Identify trends and patterns
        - Suggest specific actions to resolve issues
        
        Format your response with:
        📊 **System Status**: Overall health summary
        🔍 **Key Findings**: Important observations
        ⚠️ **Issues**: Problems that need attention
        💡 **Recommendations**: Specific actions to take
        """
    
    async def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Chat with the observability agent."""
        with tracer.start_as_current_span("adk_agent_chat"):
            try:
                # Gather observability data berdasarkan pertanyaan
                context_data = await self._gather_context_data(message)
                
                # Build comprehensive prompt
                full_prompt = f"""{self.system_prompt}

=== CURRENT SYSTEM DATA ===
{context_data}

=== USER QUESTION ===
{message}

=== INSTRUCTIONS ===
Analyze the system data above and provide a comprehensive response that:
1. Addresses the user's specific question
2. Highlights any issues or concerns found in the data
3. Provides actionable recommendations
4. Uses the specified format with emojis and sections

Respond in the same language as the user's question."""
                
                response = self.model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.error(f"Agent chat failed: {e}")
                # Detect language and return appropriate error message
                indonesian_words = ['apa', 'bagaimana', 'tampilkan', 'cek', 'ada', 'sistem', 'ringkasan']
                is_indonesian = any(word in message.lower() for word in indonesian_words)
                
                if is_indonesian:
                    return f"🚨 Maaf, terjadi error saat menganalisis sistem: {str(e)}\n\n💡 Silakan coba lagi atau periksa koneksi ke observability tools."
                else:
                    return f"🚨 Sorry, I encountered an error while analyzing the system: {str(e)}\n\n💡 Please try again or check the connection to observability tools."
    
    async def _gather_context_data(self, message: str) -> str:
        """Gather relevant observability data berdasarkan user message."""
        context = []
        message_lower = message.lower()
        
        try:
            # Always get basic health and metrics for context
            health_data = await health_check_function()
            metrics_data = await system_metrics_function()
            
            # Format health data
            if health_data.get('status') != 'error':
                overall_status = health_data.get('overall_status', 'unknown')
                components = health_data.get('components', {})
                context.append(f"SYSTEM HEALTH: {overall_status.upper()}")
                
                for comp, status in components.items():
                    comp_status = status.get('status', 'unknown')
                    context.append(f"- {comp}: {comp_status}")
            
            # Format metrics data
            if metrics_data.get('status') != 'error':
                sys_metrics = metrics_data.get('system', {})
                app_metrics = metrics_data.get('application', {})
                
                context.append(f"\nSYSTEM METRICS:")
                context.append(f"- CPU: {sys_metrics.get('cpu_percent', 0):.1f}%")
                context.append(f"- Memory: {sys_metrics.get('memory', {}).get('percent', 0):.1f}%")
                context.append(f"- Disk: {sys_metrics.get('disk', {}).get('percent', 0):.1f}%")
                
                context.append(f"\nAPPLICATION METRICS:")
                context.append(f"- Memory: {app_metrics.get('memory_mb', 0):.1f}MB")
                context.append(f"- Threads: {app_metrics.get('threads', 0)}")
                context.append(f"- Uptime: {app_metrics.get('uptime_seconds', 0)}s")
            
            # Get specific data based on keywords
            if any(word in message_lower for word in ['log', 'error', 'warning', 'issue']):
                logs_data = await query_logs_function(limit=10)
                if logs_data.get('status') in ['success', 'fallback']:
                    logs = logs_data.get('logs', [])
                    summary = logs_data.get('summary', {})
                    
                    context.append(f"\nRECENT LOGS ({len(logs)} entries):")
                    context.append(f"- Errors: {summary.get('error_count', 0)}")
                    context.append(f"- Warnings: {summary.get('warning_count', 0)}")
                    context.append(f"- Info: {summary.get('info_count', 0)}")
                    
                    # Show recent important logs
                    important_logs = [l for l in logs if l['level'] in ['ERROR', 'WARNING']][:3]
                    if important_logs:
                        context.append("\nIMPORTANT LOG ENTRIES:")
                        for log in important_logs:
                            context.append(f"- [{log['level']}] {log['message'][:100]}...")
            
            if any(word in message_lower for word in ['trace', 'slow', 'performance', 'response']):
                performance_data = await analyze_performance_function()
                if performance_data.get('status') != 'error':
                    analysis = performance_data.get('analysis', {})
                    context.append(f"\nPERFORMANCE ANALYSIS:")
                    context.append(f"- Average Response Time: {analysis.get('avg_response_time_ms', 0):.1f}ms")
                    context.append(f"- Error Count: {analysis.get('error_count', 0)}")
                    context.append(f"- Trace Count: {analysis.get('trace_count', 0)}")
                    
                    issues = analysis.get('issues', [])
                    if issues:
                        context.append("\nPERFORMANCE ISSUES:")
                        for issue in issues[:3]:
                            context.append(f"- {issue}")
                    
                    slow_ops = analysis.get('slow_operations', [])
                    if slow_ops:
                        context.append("\nSLOW OPERATIONS:")
                        for op in slow_ops[:2]:
                            context.append(f"- {op.get('duration_ms', 0):.1f}ms: {', '.join(op.get('operations', [])[:2])}")
            
        except Exception as e:
            context.append(f"\nERROR GATHERING DATA: {str(e)}")
        
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