"""
Logging utility functions for structlog operations.
"""
from typing import Any, Dict, Optional
from functools import wraps
import time

import structlog
from app.core.context import get_bound_logger, bind_structlog_context


def log_function_call(
    logger_name: str = "app.function",
    log_args: bool = False,
    log_result: bool = False,
    log_duration: bool = True,
):
    """
    Decorator to automatically log function calls with structlog.
    
    Args:
        logger_name: Name of the logger to use
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_duration: Whether to log execution duration
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_bound_logger(logger_name)
            
            # Prepare log context
            log_context = {
                "function": func.__name__,
                "module": func.__module__,
            }
            
            if log_args:
                log_context.update({
                    "args": args,
                    "kwargs": kwargs,
                })
            
            start_time = time.time()
            logger.info("Function call started", **log_context)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                success_context = {"success": True}
                if log_duration:
                    success_context["duration_ms"] = round(duration * 1000, 2)
                if log_result:
                    success_context["result"] = result
                
                logger.info("Function call completed", **log_context, **success_context)
                return result
                
            except Exception as exc:
                duration = time.time() - start_time
                
                error_context = {
                    "success": False,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                }
                if log_duration:
                    error_context["duration_ms"] = round(duration * 1000, 2)
                
                logger.error("Function call failed", **log_context, **error_context, exc_info=True)
                raise
                
        return wrapper
    return decorator


def log_with_context(**context_kwargs):
    """
    Context manager to temporarily bind additional context to structlog.
    
    Usage:
        with log_with_context(user_id="123", operation="create"):
            logger.info("User operation started")
            # ... do work ...
            logger.info("User operation completed")
    """
    class LogContext:
        def __enter__(self):
            bind_structlog_context(**context_kwargs)
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Context will be cleared by middleware
            pass
    
    return LogContext()


def get_logger_with_extra(name: str = "app", **extra_context) -> structlog.BoundLogger:
    """
    Get a structlog logger with additional context bound.
    
    Args:
        name: Logger name
        **extra_context: Additional context to bind
        
    Returns:
        Bound structlog logger
    """
    logger = get_bound_logger(name)
    if extra_context:
        logger = logger.bind(**extra_context)
    return logger


def log_database_operation(operation: str, table: Optional[str] = None, **context):
    """
    Helper to log database operations with consistent structure.
    
    Args:
        operation: Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        **context: Additional context
    """
    logger = get_bound_logger("app.database")
    
    log_context = {
        "db_operation": operation.upper(),
        "db_table": table,
        **context
    }
    
    return logger.bind(**log_context)


def log_external_api_call(service: str, endpoint: str, method: str = "GET", **context):
    """
    Helper to log external API calls with consistent structure.
    
    Args:
        service: External service name
        endpoint: API endpoint
        method: HTTP method
        **context: Additional context
    """
    logger = get_bound_logger("app.external_api")
    
    log_context = {
        "external_service": service,
        "api_endpoint": endpoint,
        "http_method": method.upper(),
        **context
    }
    
    return logger.bind(**log_context)


def log_business_event(event_type: str, entity_type: Optional[str] = None, entity_id: Optional[str] = None, **context):
    """
    Helper to log business events with consistent structure.
    
    Args:
        event_type: Type of business event
        entity_type: Type of entity involved
        entity_id: ID of the entity
        **context: Additional context
    """
    logger = get_bound_logger("app.business")
    
    log_context = {
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        **context
    }
    
    return logger.bind(**log_context)
