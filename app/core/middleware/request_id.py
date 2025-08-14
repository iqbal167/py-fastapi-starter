import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import set_request_id, clear_context


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Set in context
        set_request_id(request_id)
        
        try:
            # Add to response headers
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Clear context after request
            clear_context()
