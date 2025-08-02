# Python FastAPI Backend

A production-ready FastAPI-based Python backend template with complete observability stack and modern Python tooling.

## Features

- [FastAPI](https://fastapi.tiangolo.com/) for high-performance API development
- [UV](https://github.com/astral-sh/uv) for fast Python package management
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management
- Production-ready Docker setup with complete observability
- Complete OpenTelemetry integration with Jaeger & Tempo tracing
- Centralized logging with Fluent Bit → Loki → Grafana
- Pytest for testing with comprehensive test coverage
- Ruff for linting and formatting
- Security hardening and best practices

## Architecture

```
FastAPI Backend → OTEL Collector → Jaeger → Jaeger UI
                      ↓
                    Tempo → Grafana
     ↓
  Fluent Bit → Loki → Grafana
```

Complete observability stack with:
- **Distributed Tracing**: OpenTelemetry → Jaeger & Tempo
- **Centralized Logging**: Fluent Bit → Loki → Grafana
- **Metrics & Visualization**: Grafana dashboards
- **Real-time Monitoring**: Health checks and alerts

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
make logs
```

## Available Commands

### Local Development
```bash
make run             # Run locally with Python (hot reload)
make test            # Run tests with coverage
make lint            # Lint code with ruff
make format          # Format code with ruff
make setup-env       # Create .env from template
```

### Production Deployment
```bash
make deploy          # Complete production deployment
make compose         # Start production containers
make compose-down    # Stop containers
make health          # Check application health
make logs            # View container logs
```

### Docker Operations
```bash
make docker-build    # Build production Docker image
make docker-run      # Run production container locally
make status          # Check container status
make urls            # Show all service URLs
```

### Security & Utilities
```bash
make generate-secret # Generate secure secret key
make check-security  # Check security configuration
make info            # Show all available commands
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

Key configuration variables:
```bash
# Application
APP_NAME=FastAPI Backend
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# OpenTelemetry
OTEL_SERVICE_NAME=fastapi-backend-dev
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:14317
```

### Production Deployment
Uses `.env.example` as template with environment variable overrides:
```bash
# Set production secrets
export SECRET_KEY="$(make generate-secret)"
export DATABASE_URL="postgresql://user:pass@db:5432/myapp"

# Deploy
make deploy
```

Production configuration:
```bash
# Application
APP_NAME=FastAPI Backend
DEBUG=false
ENVIRONMENT=production

# OpenTelemetry
OTEL_SERVICE_NAME=fastapi-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

## Services

### API Service (Port 8000)
- FastAPI backend with complete observability
- Health checks and monitoring endpoints
- Security hardening with non-root user
- Resource limits and restart policies
- JSON structured logging

### Jaeger UI (Port 16686)
- **Version**: 1.57.0 (stable)
- Distributed tracing visualization
- Performance monitoring and debugging
- Request flow analysis
- Trace correlation with logs

### OTEL Collector (Ports 14317, 14318)
- **Version**: 0.100.0 (stable contrib)
- OpenTelemetry data collection and processing
- Trace aggregation and forwarding
- Memory limiting and batch processing

### Grafana (Port 3000)
- **Version**: 10.4.2 (LTS)
- Log visualization and dashboards
- Integrated with Loki for log queries
- Connected to Jaeger for trace correlation
- Pre-built "FastAPI Backend Logs" dashboard
- Default credentials: admin/admin

### Loki (Port 3100)
- **Version**: 3.0.0 (stable)
- Log aggregation and storage
- Efficient log indexing and querying
- Integration with Grafana for visualization
- Service-specific log filtering

### Fluent Bit (Port 24224)
- **Version**: 3.0.7 (stable)
- Log collection from Docker containers
- JSON log parsing and enrichment
- Forwarding logs to Loki with labels

## API Endpoints

- `GET /` - Root endpoint with application info
- `GET /health` - Health check endpoint
- `GET /settings` - Configuration endpoint (non-sensitive data)
- `GET /docs` - Interactive API documentation (development only)

Example responses:
```json
// GET /
{
  "message": "Hello World",
  "app_name": "FastAPI Backend",
  "version": "1.0.0",
  "environment": "production"
}

// GET /health
{
  "status": "healthy",
  "app_name": "FastAPI Backend",
  "version": "1.0.0",
  "environment": "production"
}
```

## Observability

### Distributed Tracing
Complete distributed tracing with OpenTelemetry:
```bash
# Access Jaeger UI
open http://localhost:16686

# Generate traces
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Centralized Logging
Structured logging with Fluent Bit → Loki → Grafana:
```bash
# Access Grafana for log visualization
open http://localhost:3000
# Default credentials: admin/admin

# View pre-built dashboard
# Navigate to: Dashboards → FastAPI Backend Logs

# Query logs directly from Loki
curl "http://localhost:3100/loki/api/v1/query_range?query={job=\"fluentbit\"}"
```

### LogQL Queries
Ready-to-use queries for log analysis:
```logql
# All backend logs
{job="fluentbit", service_name="fastapi-backend"} | json

# Error logs only
{job="fluentbit", service_name="fastapi-backend"} | json | level="ERROR"

# Request logs with formatting
{job="fluentbit", service_name="fastapi-backend"} | json | line_format "{{.method}} {{.url}} → {{.status_code}} ({{.duration_ms}}ms)"

# Request rate metrics
sum(rate({job="fluentbit", service_name="fastapi-backend"} | json [5m]))
```

### Health Monitoring
```bash
# Check application health
make health

# Detailed health check
curl http://localhost:8000/health

# Check all container status
make status

# Show all service URLs
make urls
```

## Security Features

- **Non-root containers**: All containers run as non-root users
- **Resource limits**: CPU and memory limits for stability
- **Secret management**: Secure secret key generation
- **Environment validation**: Production settings validation
- **Network isolation**: Custom Docker network (`fastapi-backend-network`)
- **Health checks**: Built-in health monitoring
- **Structured logging**: JSON logs with request correlation

## Development Workflow

```bash
# Daily development
make run              # Start local development server
# Make code changes (automatic reload enabled)
make test             # Run tests with coverage
make lint             # Check code quality

# Test production build
make deploy           # Test production deployment
make health           # Verify deployment
make logs             # Monitor logs
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
make status

# Access services
open http://localhost:8000      # API
open http://localhost:16686     # Jaeger
open http://localhost:3000      # Grafana

# Monitor logs
make logs
```

### Security Checklist
```bash
# Check security configuration
make check-security

# Ensure:
# ✅ SECRET_KEY is set securely
# ✅ DEBUG is disabled in production
# ✅ Production database is configured
# ✅ Log level is appropriate
# ✅ All containers run as non-root
```

## File Structure

```
├── app/                                    # Application code
│   ├── main.py                            # FastAPI application
│   ├── core/                              # Core functionality
│   │   ├── settings.py                    # Configuration management
│   │   ├── middleware.py                  # Custom middleware
│   │   └── logging.py                     # Logging configuration
│   └── api/                               # API routes
├── tests/                                 # Test files
├── scripts/                               # Configuration scripts
│   ├── opentelemetry/                     # OTEL configuration
│   │   └── otel-collector-config.yaml    # OTEL Collector config
│   └── logging/                           # Logging configuration
│       ├── fluent-bit.conf               # Fluent Bit config
│       ├── grafana-datasources.yaml     # Grafana datasources
│       └── dashboards/                   # Pre-built dashboards
├── Dockerfile                             # Production-ready Docker image
├── docker-compose.yml                     # Production services
├── .env.example                          # Production template
├── run.py                                # Application entry point
├── Makefile                              # Development commands
├── pyproject.toml                        # Python project configuration
└── README.md                             # This file
```

## Testing

```bash
# Run all tests with coverage
make test

# Run specific test file
uv run pytest tests/test_main.py -v

# Run with detailed coverage report
uv run pytest --cov=app --cov-report=html tests/

# Run tests in watch mode (development)
uv run pytest-watch
```

## Troubleshooting

### Container Issues
```bash
# Check container status
make status

# View all logs
make logs

# Restart services
make compose-down && make deploy
```

### Health Check Issues
```bash
# Test health endpoints
make health
curl http://localhost:13133  # OTEL Collector health

# Check health configuration
docker compose config | grep -A 5 healthcheck
```

### Logging Issues
```bash
# Check log pipeline
curl "http://localhost:3100/ready"  # Loki readiness
curl "http://localhost:3100/loki/api/v1/label/job/values"  # Available jobs

# Test log queries
curl "http://localhost:3100/loki/api/v1/query_range?query={job=\"fluentbit\"}"

# Check Fluent Bit status
docker compose logs fluent-bit
```

### Application Issues
```bash
# Check application logs
make logs

# Test configuration
curl http://localhost:8000/settings

# Debug environment
docker compose exec api env | grep -E "(APP_|OTEL_|DEBUG)"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `make test`
5. Lint code: `make lint`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Submit a pull request

## Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## Package Information

- **Package Name**: `py-fastapi-backend`
- **Service Name**: `fastapi-backend`
- **Network**: `fastapi-backend-network`
- **Python Version**: 3.11+
- **FastAPI Version**: 0.116.1+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Production-ready FastAPI backend with complete observability! 🚀**

Ready for deployment with monitoring, logging, tracing, and security best practices built-in.
