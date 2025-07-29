# Python Backend Starter

A production-ready FastAPI-based Python backend starter template with complete observability stack and modern Python tooling.

## Features

- [FastAPI](https://fastapi.tiangolo.com/) for high-performance API development
- [UV](https://github.com/astral-sh/uv) for fast Python package management
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management
- Production-ready Docker setup with observability
- Complete OpenTelemetry integration with Jaeger tracing
- Pytest for testing with comprehensive test coverage
- Ruff for linting and formatting
- Security hardening and best practices

## Architecture

```
FastAPI App → OTEL Collector → Jaeger → Jaeger UI
```

## Requirements

- Python >= 3.11
- UV package manager
- Docker & Docker Compose (for production deployment)

## Quick Start

### Local Development
```bash
# Setup environment
make setup-env

# Install dependencies
uv venv
uv pip install -e ".[dev]"

# Run locally (recommended for development)
make run

# Run tests
make test

# Lint and format
make lint
make format
```

### Production Deployment
```bash
# Generate secure secret key
export SECRET_KEY="$(make generate-secret)"

# Deploy production environment
make deploy

# Check health
make health

# View logs
make compose-logs
```

## Available Commands

### Local Development
```bash
make run             # Run locally with Python (hot reload)
make test            # Run tests
make lint            # Lint code
make format          # Format code
```

### Production Deployment
```bash
make deploy          # Complete production deployment
make compose         # Start production containers
make compose-down    # Stop containers
make health          # Check application health
make logs            # View container logs
```

### Setup & Security
```bash
make setup-env       # Create .env from template
make generate-secret # Generate secure secret key
make check-security  # Check security configuration
```

### Information
```bash
make info            # Show all available commands
make help            # Same as info
```

## Configuration

### Local Development
Uses `.env` file for local development settings:
```bash
# Setup environment file
make setup-env

# Edit for local development
vim .env
```

### Production Deployment
Uses `.env.example` as template in container with environment variable overrides:
```bash
# Set production secrets
export SECRET_KEY="$(make generate-secret)"
export DATABASE_URL="postgresql://user:pass@db:5432/myapp"

# Deploy
make deploy
```

## Services

### API Service (Port 8000)
- FastAPI application with complete observability
- Health checks and monitoring endpoints
- Security hardening with non-root user
- Resource limits and restart policies

### Jaeger UI (Port 16686)
- Distributed tracing visualization
- Performance monitoring and debugging
- Request flow analysis

### OTEL Collector (Ports 14317, 14318)
- OpenTelemetry data collection and processing
- Trace aggregation and forwarding
- Memory limiting and batch processing

## Endpoints

- `GET /` - Root endpoint with application info
- `GET /health` - Health check endpoint
- `GET /settings` - Configuration endpoint (non-sensitive data)
- `GET /docs` - Interactive API documentation (development only)

## Observability

### Tracing
Complete distributed tracing with OpenTelemetry:
```bash
# Access Jaeger UI
open http://localhost:16686

# Generate traces
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Health Monitoring
```bash
# Check application health
make health

# Detailed health check
make health-detailed

# Check all container status
make status
```

### Logging
```bash
# View application logs
make logs-api

# View all service logs
make logs

# Follow logs in real-time
docker compose logs -f api
```

## Security Features

- **Non-root containers**: All containers run as non-root users
- **Resource limits**: CPU and memory limits for stability
- **Secret management**: Secure secret key generation
- **Environment validation**: Production settings validation
- **Network isolation**: Custom Docker networks
- **Health checks**: Built-in health monitoring

## Development Workflow

```bash
# Daily development
make run              # Start local development
# Make code changes (automatic reload)
make test             # Run tests
make lint             # Check code quality

# Test production build
make deploy           # Test production deployment
make health           # Verify deployment
make compose-down     # Stop containers
```

## Production Deployment

### Prerequisites
```bash
# Generate secure secrets
export SECRET_KEY="$(make generate-secret)"

# Set production database (optional)
export DATABASE_URL="postgresql://user:pass@prod-db:5432/myapp"

# Set log level (optional)
export LOG_LEVEL="WARNING"
```

### Deploy
```bash
# Complete production deployment
make deploy

# Verify deployment
make health
open http://localhost:16686

# Monitor
make logs-api
```

### Security Checklist
```bash
# Check security configuration
make check-security

# Ensure:
# ✅ SECRET_KEY is set securely
# ✅ DEBUG is disabled
# ✅ Production database is configured
# ✅ Log level is appropriate
```

## File Structure

```
├── app/                                    # Application code
│   ├── main.py                            # FastAPI application
│   ├── core/                              # Core functionality
│   │   ├── settings.py                    # Configuration management
│   │   ├── middleware.py                  # Custom middleware
│   │   └── ...
│   └── ...
├── tests/                                 # Test files
├── scripts/opentelemetry/                 # OTEL configuration
│   └── otel-collector-config.yaml        # OTEL Collector config
├── docs/                                  # Documentation
│   ├── DOCKER.md                         # Docker guide
│   └── CONFIGURATION.md                   # Configuration guide
├── Dockerfile                             # Production-ready Docker image
├── docker-compose.yml                     # Production services
├── .env                                   # Local development config
├── .env.example                          # Production template
├── run.py                                # Application entry point
├── Makefile                              # Development commands
├── pyproject.toml                        # Python project configuration
└── README.md                             # This file
```

## Testing

```bash
# Run all tests
make test

# Run specific test file
uv run pytest tests/test_main.py -v

# Run with coverage
uv run pytest --cov=app tests/
```

## Troubleshooting

### Container Issues
```bash
# Check container status
make status

# View logs
make logs

# Restart services
docker compose restart
```

### Health Check Issues
```bash
# Test health endpoints
make health
curl http://localhost:13133  # OTEL Collector health

# Check health configuration
docker compose config | grep -A 5 healthcheck
```

### Application Issues
```bash
# Check application logs
make logs-api

# Test settings
docker compose exec api python -c "from app.core.settings import settings; print(settings.environment)"

# Debug configuration
make check-security
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Lint code: `make lint`
6. Submit a pull request

## Documentation

- [Docker Guide](docs/DOCKER.md) - Complete Docker setup guide
- [Configuration Guide](docs/CONFIGURATION.md) - Environment configuration
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## License

This project is licensed under the MIT License.

---

**Production-ready FastAPI starter with complete observability! 🚀**
