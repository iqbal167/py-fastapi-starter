from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Settings are loaded from:
    1. Environment variables
    2. .env file
    3. Default values
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application Configuration
    app_name: str = Field(default="FastAPI Backend", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")

    # API Configuration
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time in minutes"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./app.db", description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # Redis Configuration (Optional)
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_password: Optional[str] = Field(default=None, description="Redis password")

    # OpenTelemetry Configuration
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:14317", description="OpenTelemetry OTLP endpoint"
    )
    otel_service_name: str = Field(
        default="fastapi-backend", description="OpenTelemetry service name"
    )
    otel_service_version: str = Field(
        default="0.1.0", description="OpenTelemetry service version"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")

    # External Services (Optional)
    external_api_url: Optional[str] = Field(
        default=None, description="External API URL"
    )
    external_api_key: Optional[str] = Field(
        default=None, description="External API key"
    )

    # Computed properties for CORS (not from env vars)
    @property
    def allowed_hosts(self) -> List[str]:
        """Allowed hosts for CORS - computed based on environment."""
        if self.is_production:
            # In production, you should specify actual domains
            return ["yourdomain.com", "www.yourdomain.com"]
        return ["*"]  # Allow all in development

    @property
    def allowed_origins(self) -> List[str]:
        """Allowed origins for CORS - computed based on environment."""
        if self.is_production:
            # In production, specify actual frontend URLs
            return ["https://yourdomain.com", "https://www.yourdomain.com"]
        return ["*"]  # Allow all in development

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate critical settings in production
        if self.environment == "production":
            self._validate_production_settings()

    def _validate_production_settings(self):
        """Validate critical settings for production environment."""
        if self.secret_key == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set in production environment")

        if self.debug:
            raise ValueError("DEBUG must be False in production environment")

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency function to get settings instance.
    Useful for FastAPI dependency injection.
    """
    return settings
