"""
Utility modules for the FastAPI application.
"""

# Logging utilities
from .logging import (
    log_function_call,
    log_with_context,
    get_logger_with_extra,
    log_database_operation,
    log_external_api_call,
    log_business_event,
)

# Log parsing utilities
from .log_parser import (
    LogEntry,
    LogParser,
    parse_log_file,
    parse_log_string,
    analyze_request_performance,
    find_slow_requests,
    find_error_patterns,
)

# Lifespan utilities
from .lifespan import (
    LifespanManager,
    lifespan_manager,
    startup,
    shutdown,
    create_database_lifespan_manager,
    create_full_stack_lifespan_manager,
    get_application_health,
)

# Common utilities
from .common import (
    generate_uuid,
    generate_short_id,
    generate_hash,
    utc_now,
    safe_dict_get,
    sanitize_string,
    mask_sensitive_data,
    format_bytes,
    format_duration,
    chunk_list,
    deep_merge_dicts,
)

__all__ = [
    # Logging utilities
    "log_function_call",
    "log_with_context", 
    "get_logger_with_extra",
    "log_database_operation",
    "log_external_api_call",
    "log_business_event",
    # Log parsing utilities
    "LogEntry",
    "LogParser",
    "parse_log_file",
    "parse_log_string",
    "analyze_request_performance",
    "find_slow_requests",
    "find_error_patterns",
    # Lifespan utilities
    "LifespanManager",
    "lifespan_manager",
    "startup",
    "shutdown",
    "create_database_lifespan_manager",
    "create_full_stack_lifespan_manager",
    "get_application_health",
    # Common utilities
    "generate_uuid",
    "generate_short_id",
    "generate_hash",
    "utc_now",
    "safe_dict_get",
    "sanitize_string",
    "mask_sensitive_data",
    "format_bytes",
    "format_duration",
    "chunk_list",
    "deep_merge_dicts",
]
