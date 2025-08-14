import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger
from app.core.context import bind_context


class LoggingMiddleware(BaseHTTPMiddleware):
    def _get_event_type(self, method: str, path: str, status_code: int) -> str:
        """Generate event_type based on route and method."""
        # Clean path (remove leading slash and replace slashes with dots)
        clean_path = path.lstrip('/').replace('/', '.')
        
        # Handle root path
        if not clean_path:
            clean_path = "root"
        
        # Convert method to lowercase
        method_lower = method.lower()
        
        # Simple format: {path}.{method}
        return f"{clean_path}.{method_lower}"

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate event_type for this request
        event_type = self._get_event_type(request.method, request.url.path, 200)
        
        # Bind request context including event_type
        bind_context(
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            event_type=event_type,
        )
        
        logger = get_logger("app.request")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Simple success log - event_type already in context
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            
            return response
            
        except Exception as exc:
            duration = time.time() - start_time
            
            # Simple error log - event_type already in context
            logger.error(
                "Request failed",
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
                exc_info=True
            )
            
            raise
