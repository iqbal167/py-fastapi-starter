#!/usr/bin/env python3
"""
Run script for FastAPI application with clean logging configuration.
"""
import uvicorn
from app.core.settings import settings


def main():
    """Run the application with clean logging configuration."""
    
    # Clean uvicorn configuration
    uvicorn_config = {
        "app": "app.main:app",
        "host": settings.host,
        "port": settings.port,
        "reload": settings.reload and settings.is_development,
        "log_level": settings.log_level.lower(),
        # Disable uvicorn access log to prevent mixed logging
        "access_log": False,
        # Use our custom log config
        "log_config": None,
        # Disable uvicorn's default logging setup
        "use_colors": False,
    }
    
    print(f"📊 Environment: {settings.environment}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"📝 Log level: {settings.log_level}")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print("📋 All logs will be in structured JSON format")
    print("-" * 50)
    
    # Run the application
    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
