import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger
from app.core.context import get_request_id


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            "Finished processing request",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host,
                "request_id": get_request_id(),
            },
        )

        return response
