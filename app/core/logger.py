import structlog

# Configure JSON logging
structlog.configure(
    processors=[structlog.processors.JSONRenderer()]
)


def get_logger(name: str = "app"):
    """Get logger with context."""
    from app.core.context import get_request_id, get_context
    
    logger = structlog.get_logger(name)
    
    # Add request ID
    request_id = get_request_id()
    if request_id:
        logger = logger.bind(request_id=request_id)
    
    # Add other context
    context = get_context()
    if context:
        logger = logger.bind(**context)
    
    return logger
