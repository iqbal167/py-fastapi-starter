import logging
from pythonjsonlogger import json as jsonlogger
from app.core.settings import settings

logging.getLogger("uvicorn.error").name = "app.uvicorn"


class CleanJSONFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        log_record.pop("color_message", None)
        return super().process_log_record(log_record)


def setup_logger() -> logging.Logger:
    """Setup logger with configuration from settings."""
    formatter = CleanJSONFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp",
            "message": "msg",
        },
    )

    logger = logging.getLogger("app")
    # Use log level from settings
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Configure uvicorn loggers
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        uv_logger.propagate = False
        uv_handler = logging.StreamHandler()
        uv_handler.setFormatter(formatter)
        uv_logger.addHandler(uv_handler)

    # Deactivate access logger in production
    access_logger = logging.getLogger("uvicorn.access")
    if settings.is_production:
        access_logger.handlers.clear()
        access_logger.setLevel(logging.WARNING)
        access_logger.propagate = False

    return logger


# Initialize logger
logger = setup_logger()
