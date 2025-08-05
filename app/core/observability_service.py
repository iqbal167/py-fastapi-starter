"""
Observability service untuk mengintegrasikan logs, traces, dan metrics
dengan Google ADK Agent untuk chat-based monitoring.
"""
import json
import logging
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.settings import settings

logger = logging.getLogger(__name__)


class ObservabilityService:
    """Service untuk mengakses data observability dari berbagai sumber."""
    
    def __init__(self):
        self.loki_url = "http://localhost:3100"
        self.jaeger_url = "http://localhost:16686"
        self.grafana_url = "http://localhost:3000"
        self.otel_collector_url = "http://localhost:13133"
    
    async def query_logs(self, query: str = None, level: str = None, 
                        limit: int = 100, hours_back: int = 1) -> Dict[str, Any]:
        """Query logs dari Loki dengan LogQL."""
        try:
            # Build LogQL query
            base_query = '{job="fluentbit"}'
            
            if level:
                base_query += f' | json | level="{level.upper()}"'
            elif query:
                base_query += f' | json | message |~ "(?i){query}"'
            else:
                base_query += ' | json'
            
            # Time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            params = {
                'query': base_query,
                'start': int(start_time.timestamp() * 1000000000),
                'end': int(end_time.timestamp() * 1000000000),
                'limit': limit,
                'direction': 'backward'
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.loki_url}/loki/api/v1/query_range",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logs = []
                    
                    for stream in data.get('data', {}).get('result', []):
                        for entry in stream.get('values', []):
                            timestamp_ns, log_line = entry
                            timestamp = datetime.fromtimestamp(int(timestamp_ns) / 1000000000)
                            
                            # Parse log line
                            try:
                                if log_line.startswith('{'):
                                    log_data = json.loads(log_line)
                                    message = log_data.get('log', log_data.get('message', log_line))
                                    level_val = 'INFO'
                                    
                                    # Extract level from message if available
                                    if 'ERROR' in message.upper():
                                        level_val = 'ERROR'
                                    elif 'WARNING' in message.upper() or 'WARN' in message.upper():
                                        level_val = 'WARNING'
                                    elif 'DEBUG' in message.upper():
                                        level_val = 'DEBUG'
                                else:
                                    message = log_line
                                    level_val = 'INFO'
                                
                                logs.append({
                                    'timestamp': timestamp.isoformat(),
                                    'level': level_val,
                                    'message': message.strip(),
                                    'service': settings.otel_service_name
                                })
                            except:
                                logs.append({
                                    'timestamp': timestamp.isoformat(),
                                    'level': 'INFO',
                                    'message': log_line.strip(),
                                    'service': settings.otel_service_name
                                })
                    
                    # Sort by timestamp descending
                    logs.sort(key=lambda x: x['timestamp'], reverse=True)
                    
                    return {
                        'status': 'success',
                        'query': base_query,
                        'total_logs': len(logs),
                        'logs': logs[:limit],
                        'summary': {
                            'error_count': len([l for l in logs if l['level'] == 'ERROR']),
                            'warning_count': len([l for l in logs if l['level'] == 'WARNING']),
                            'info_count': len([l for l in logs if l['level'] == 'INFO'])
                        },
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        }
                    }
                else:
                    # Fallback: return mock data if Loki not available
                    return {
                        'status': 'fallback',
                        'logs': [
                            {
                                'timestamp': datetime.now().isoformat(),
                                'level': 'INFO',
                                'message': 'Application started successfully',
                                'service': settings.otel_service_name
                            },
                            {
                                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                                'level': 'INFO', 
                                'message': 'Health check endpoint accessed',
                                'service': settings.otel_service_name
                            }
                        ],
                        'total_logs': 2,
                        'summary': {'error_count': 0, 'warning_count': 0, 'info_count': 2},
                        'note': 'Loki not available, showing sample data'
                    }
                    
        except Exception as e:
            logger.error(f"Error querying logs: {e}")
            # Return fallback data
            return {
                'status': 'fallback',
                'logs': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'level': 'INFO',
                        'message': 'System is running normally',
                        'service': settings.otel_service_name
                    }
                ],
                'total_logs': 1,
                'summary': {'error_count': 0, 'warning_count': 0, 'info_count': 1},
                'note': f'Log query failed: {str(e)}'
            }
    
    async def query_traces(self, service: str = None, operation: str = None, 
                          limit: int = 20, hours_back: int = 1) -> Dict[str, Any]:
        """Query traces dari Jaeger."""
        try:
            service_name = service or settings.otel_service_name
            
            # Time range in microseconds
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            params = {
                'service': service_name,
                'start': int(start_time.timestamp() * 1000000),  # microseconds
                'end': int(end_time.timestamp() * 1000000),
                'limit': limit
            }
            
            if operation:
                params['operation'] = operation
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.jaeger_url}/api/traces",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    traces = []
                    
                    for trace in data.get('data', []):
                        trace_info = {
                            'trace_id': trace.get('traceID'),
                            'spans': len(trace.get('spans', [])),
                            'duration_ms': trace.get('spans', [{}])[0].get('duration', 0) / 1000,
                            'start_time': datetime.fromtimestamp(
                                trace.get('spans', [{}])[0].get('startTime', 0) / 1000000
                            ).isoformat() if trace.get('spans') else None,
                            'operations': list(set([
                                span.get('operationName') 
                                for span in trace.get('spans', [])
                            ])),
                            'services': list(set([
                                span.get('process', {}).get('serviceName')
                                for span in trace.get('spans', [])
                            ]))
                        }
                        traces.append(trace_info)
                    
                    return {
                        'status': 'success',
                        'service': service_name,
                        'total_traces': len(traces),
                        'traces': traces,
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        }
                    }
                else:
                    return {
                        'status': 'error',
                        'error': f"Jaeger query failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error querying traces: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Dapatkan ringkasan metrics dari berbagai sumber."""
        try:
            import psutil
            import os
            
            # System metrics
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
                    'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
                    'percent': psutil.disk_usage('/').percent
                },
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Application metrics
            process = psutil.Process(os.getpid())
            app_metrics = {
                'pid': os.getpid(),
                'cpu_percent': process.cpu_percent(),
                'memory_mb': round(process.memory_info().rss / (1024**2), 2),
                'threads': process.num_threads(),
                'connections': len(process.connections()),
                'uptime_seconds': int(datetime.now().timestamp() - process.create_time())
            }
            
            # Check service health
            services_health = await self._check_services_health()
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'system': system_metrics,
                'application': app_metrics,
                'services': services_health
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _check_services_health(self) -> Dict[str, Any]:
        """Check health dari berbagai services observability."""
        services = {}
        
        # Check Loki
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.loki_url}/ready")
                services['loki'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'url': self.loki_url
                }
        except:
            services['loki'] = {'status': 'unhealthy', 'url': self.loki_url}
        
        # Check Jaeger
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.jaeger_url}/api/services")
                services['jaeger'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'url': self.jaeger_url
                }
        except:
            services['jaeger'] = {'status': 'unhealthy', 'url': self.jaeger_url}
        
        # Check OTEL Collector
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.otel_collector_url}")
                services['otel_collector'] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'url': self.otel_collector_url
                }
        except:
            services['otel_collector'] = {'status': 'unhealthy', 'url': self.otel_collector_url}
        
        return services
    
    async def analyze_performance(self, hours_back: int = 1) -> Dict[str, Any]:
        """Analisis performa berdasarkan logs dan traces."""
        try:
            # Get error logs
            error_logs = await self.query_logs(level="ERROR", hours_back=hours_back)
            warning_logs = await self.query_logs(level="WARNING", hours_back=hours_back)
            
            # Get traces
            traces = await self.query_traces(hours_back=hours_back)
            
            # Get metrics
            metrics = await self.get_metrics_summary()
            
            # Analyze
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'time_range_hours': hours_back,
                'error_count': len(error_logs.get('logs', [])),
                'warning_count': len(warning_logs.get('logs', [])),
                'trace_count': len(traces.get('traces', [])),
                'avg_response_time_ms': 0,
                'slow_operations': [],
                'issues': []
            }
            
            # Calculate average response time
            if traces.get('traces'):
                durations = [t['duration_ms'] for t in traces['traces'] if t['duration_ms']]
                if durations:
                    analysis['avg_response_time_ms'] = round(sum(durations) / len(durations), 2)
                    
                    # Find slow operations (> 1000ms)
                    slow_traces = [t for t in traces['traces'] if t['duration_ms'] > 1000]
                    analysis['slow_operations'] = slow_traces[:5]  # Top 5
            
            # Identify issues
            if analysis['error_count'] > 0:
                analysis['issues'].append(f"Found {analysis['error_count']} error(s) in the last {hours_back} hour(s)")
            
            if analysis['avg_response_time_ms'] > 500:
                analysis['issues'].append(f"Average response time is high: {analysis['avg_response_time_ms']}ms")
            
            if metrics.get('system', {}).get('cpu_percent', 0) > 80:
                analysis['issues'].append(f"High CPU usage: {metrics['system']['cpu_percent']}%")
            
            if metrics.get('system', {}).get('memory', {}).get('percent', 0) > 80:
                analysis['issues'].append(f"High memory usage: {metrics['system']['memory']['percent']}%")
            
            return {
                'status': 'success',
                'analysis': analysis,
                'raw_data': {
                    'error_logs': error_logs,
                    'traces': traces,
                    'metrics': metrics
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Global instance
observability_service = ObservabilityService()