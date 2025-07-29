.PHONY: run compose test lint format docker-build docker-run clean help act

# Local development
run:
	@echo "🚀 Starting FastAPI application locally..."
	@uv run python run.py

test:
	@echo "🧪 Running tests..."
	@uv run pytest

lint:
	@echo "🔍 Linting code..."
	@uv run ruff check . --fix

format:
	@echo "✨ Formatting code..."
	@uv run ruff format .

# GitHub Actions local testing with act
act:
	@echo "🎭 Running GitHub Actions locally with act..."
	@act --secret-file .act.secrets --workflows .github/workflows/ci.yml --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest --job test --env UV_HTTP_TIMEOUT=30

act-list:
	@echo "📋 Listing available GitHub Actions workflows..."
	@act --secret-file .act.secrets --list

act-dry-run:
	@echo "🔍 Dry run of GitHub Actions workflows..."
	@act --secret-file .act.secrets --workflows .github/workflows/ci.yml --container-architecture linux/amd64 -P ubuntu-latest=catthehacker/ubuntu:act-latest --job test --env UV_HTTP_TIMEOUT=30 --dry-run

# Docker production deployment
compose:
	@echo "🐳 Starting production environment with Docker Compose..."
	@docker compose up --build -d

compose-down:
	@echo "🛑 Stopping Docker environment..."
	@docker compose down

compose-logs:
	@echo "📋 Showing container logs..."
	@docker compose logs -f

compose-restart:
	@echo "🔄 Restarting Docker environment..."
	@docker compose restart

# Docker build
docker-build:
	@echo "🔨 Building production Docker image..."
	@docker build -t fastapi-backend:latest .

docker-run:
	@echo "🐳 Running production container..."
	@docker run -p 8000:8000 --env-file .env fastapi-backend:latest

# Health checks
health:
	@echo "🏥 Checking application health..."
	@curl -f http://localhost:8000/health && echo " ✅ Healthy" || echo " ❌ Unhealthy"

health-detailed:
	@echo "🏥 Detailed health check..."
	@curl -s http://localhost:8000/health | jq '.' || echo "❌ Health check failed or jq not installed"

# Monitoring
status:
	@echo "📊 Docker Compose Status:"
	@docker compose ps

logs:
	@echo "📋 Recent logs:"
	@docker compose logs --tail=50

# Observability URLs
urls:
	@echo "🌐 Observability Stack URLs:"
	@echo "📱 API: http://localhost:8000"
	@echo "🔍 API Health: http://localhost:8000/health"
	@echo "📊 Jaeger UI: http://localhost:16686"
	@echo "📈 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📋 Loki API: http://localhost:3100"
	@echo "🔧 Fluent Bit: http://localhost:2020"

# Cleanup
clean:
	@echo "🧹 Cleaning up Docker resources..."
	@docker system prune -f
	@docker volume prune -f

clean-all:
	@echo "🧹 Deep cleaning Docker resources (including images)..."
	@docker system prune -af
	@docker volume prune -f

# Complete deployment workflow
deploy: compose
	@echo "⏳ Waiting for services to be ready..."
	@sleep 20
	@make health
	@echo ""
	@echo "🎉 Production environment is ready!"
	@echo "📱 API: http://localhost:8000"
	@echo "🔍 API Health: http://localhost:8000/health"
	@echo "📊 Jaeger UI: http://localhost:16686"
	@echo "📈 Grafana: http://localhost:3000 (admin/admin)"
	@echo "📋 Loki API: http://localhost:3100"
	@echo ""
	@echo "📋 Useful commands:"
	@echo "   make urls           - Show all service URLs"
	@echo "   make logs           - View recent logs"
	@echo "   make logs-api       - Follow API logs"
	@echo "   make status         - Check container status"
	@echo "   make health         - Check application health"
	@echo "   make compose-down   - Stop environment"

# Environment setup
setup-env:
	@echo "⚙️ Setting up environment file..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env from .env.example"; \
		echo "⚠️  Please update .env with your production values!"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Security helpers
generate-secret:
	@echo "🔐 Generating secure secret key..."
	@openssl rand -hex 32

check-security:
	@echo "🔒 Security checklist:"
	@if grep -q "your-super-secret-key-change-in-production-please" .env 2>/dev/null; then \
		echo "❌ SECRET_KEY still uses default value!"; \
	else \
		echo "✅ SECRET_KEY appears to be customized"; \
	fi
	@if grep -q "DEBUG=false" .env 2>/dev/null; then \
		echo "✅ DEBUG is disabled"; \
	else \
		echo "⚠️  DEBUG should be false in production"; \
	fi

# Information
info:
	@echo "📋 FastAPI Backend - Production Ready Commands:"
	@echo ""
	@echo "🛠️  Local Development:"
	@echo "   make run             - Run locally with Python"
	@echo "   make test            - Run tests"
	@echo "   make lint            - Lint code"
	@echo "   make format          - Format code"
	@echo ""
	@echo "🎭 GitHub Actions (Local Testing):"
	@echo "   make act             - Run GitHub Actions locally with act"
	@echo "   make act-list        - List available workflows"
	@echo "   make act-dry-run     - Dry run of workflows"
	@echo ""
	@echo "🐳 Docker Production:"
	@echo "   make deploy          - Complete deployment (recommended)"
	@echo "   make compose         - Start containers"
	@echo "   make compose-down    - Stop containers"
	@echo "   make compose-restart - Restart containers"
	@echo ""
	@echo "📊 Monitoring & Observability:"
	@echo "   make urls            - Show all service URLs"
	@echo "   make health          - Check application health"
	@echo "   make status          - Check container status"
	@echo "   make logs            - View recent logs"
	@echo "   make logs-api        - Follow API logs"
	@echo "   make logs-fluent-bit - Follow Fluent Bit logs"
	@echo "   make logs-loki       - Follow Loki logs"
	@echo "   make logs-grafana    - Follow Grafana logs"
	@echo ""
	@echo "🔨 Docker Build:"
	@echo "   make docker-build    - Build production image"
	@echo "   make docker-run      - Run single container"
	@echo ""
	@echo "⚙️  Setup:"
	@echo "   make setup-env       - Create .env from template"
	@echo "   make generate-secret - Generate secure secret key"
	@echo "   make check-security  - Check security configuration"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "   make clean           - Clean Docker resources"
	@echo "   make clean-all       - Deep clean (including images)"

help: info

# Default target
.DEFAULT_GOAL := info
