import pytest
from app.core.settings import Settings


def test_settings_default_values():
    """Test that settings have correct default values when no env vars are set."""
    # Create settings without loading from .env file
    settings = Settings(_env_file=None)

    assert settings.app_name == "FastAPI Backend"
    assert settings.app_version == "0.1.0"
    assert settings.debug is False
    assert settings.environment == "development"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.secret_key == "your-secret-key-change-in-production"
    assert settings.access_token_expire_minutes == 30
    assert settings.algorithm == "HS256"
    assert settings.database_url == "sqlite:///./app.db"
    assert settings.database_echo is False
    assert settings.otel_exporter_otlp_endpoint == "http://localhost:14317"
    assert settings.otel_service_name == "fastapi-backend"
    assert settings.otel_service_version == "0.1.0"
    assert settings.log_level == "INFO"


def test_settings_from_env_vars(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    # Clear any existing env vars that might interfere
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Set test env vars
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Test App"
    assert settings.debug is True
    assert settings.port == 9000
    assert settings.environment == "testing"
    assert settings.secret_key == "test-secret-key"
    assert settings.database_url == "postgresql://test:test@localhost/test"


def test_settings_environment_properties():
    """Test environment property methods."""
    # Test development
    settings = Settings(environment="development", _env_file=None)
    assert settings.is_development is True
    assert settings.is_production is False
    assert settings.is_testing is False

    # Test production
    settings = Settings(
        environment="production", secret_key="secure-key", debug=False, _env_file=None
    )
    assert settings.is_development is False
    assert settings.is_production is True
    assert settings.is_testing is False

    # Test testing
    settings = Settings(environment="testing", _env_file=None)
    assert settings.is_development is False
    assert settings.is_production is False
    assert settings.is_testing is True


def test_cors_settings():
    """Test CORS settings computed properties."""
    # Development environment
    dev_settings = Settings(environment="development", _env_file=None)
    assert dev_settings.allowed_origins == ["*"]
    assert dev_settings.allowed_hosts == ["*"]

    # Production environment
    prod_settings = Settings(
        environment="production", secret_key="secure-key", debug=False, _env_file=None
    )
    assert prod_settings.allowed_origins != ["*"]
    assert prod_settings.allowed_hosts != ["*"]
    assert isinstance(prod_settings.allowed_origins, list)
    assert isinstance(prod_settings.allowed_hosts, list)


def test_optional_settings():
    """Test optional settings with None defaults."""
    settings = Settings(_env_file=None)

    assert settings.redis_url is None
    assert settings.redis_password is None
    assert settings.external_api_url is None
    assert settings.external_api_key is None


def test_optional_settings_with_values(monkeypatch):
    """Test optional settings when values are provided."""
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("REDIS_PASSWORD", "redis-pass")
    monkeypatch.setenv("EXTERNAL_API_URL", "https://api.example.com")
    monkeypatch.setenv("EXTERNAL_API_KEY", "api-key-123")

    settings = Settings(_env_file=None)

    assert settings.redis_url == "redis://localhost:6379"
    assert settings.redis_password == "redis-pass"
    assert settings.external_api_url == "https://api.example.com"
    assert settings.external_api_key == "api-key-123"


def test_production_validation():
    """Test that production environment validates critical settings."""
    # Should raise error with default secret key
    with pytest.raises(ValueError, match="SECRET_KEY must be set in production"):
        Settings(environment="production", debug=False, _env_file=None)

    # Should raise error with debug=True
    with pytest.raises(ValueError, match="DEBUG must be False in production"):
        Settings(
            environment="production",
            secret_key="secure-key",
            debug=True,
            _env_file=None,
        )

    # Should work with proper settings
    settings = Settings(
        environment="production", secret_key="secure-key", debug=False, _env_file=None
    )
    assert settings.is_production is True
