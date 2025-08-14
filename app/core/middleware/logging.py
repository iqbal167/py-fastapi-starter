import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import get_logger
from app.core.context import bind_context


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):        
        start_time = time.time()
        
        # Bind request context
        bind_context(
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )
        
        logger = get_logger("app.request")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log request completion
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
            )
            
            return response
            
        except Exception as exc:
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                "Request failed",
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
                exc_info=True
            )
            
            raise
