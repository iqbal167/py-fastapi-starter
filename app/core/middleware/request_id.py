import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import set_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        set_request_id(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id  # optional, for tracing back
        return response
