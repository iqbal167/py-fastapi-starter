from contextvars import ContextVar
from typing import Optional, Dict, Any

# Context variables
_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_context: ContextVar[Dict[str, Any]] = ContextVar("context", default={})


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def get_request_id() -> Optional[str]:
    return _request_id.get()


def bind_context(**kwargs) -> None:
    current = _context.get({})
    current.update(kwargs)
    _context.set(current)


def clear_context() -> None:
    _context.set({})


def get_context() -> Dict[str, Any]:
    """Get current context data."""
    return _context.get({})
