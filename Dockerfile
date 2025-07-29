# Production-ready Dockerfile for FastAPI application

# Builder stage
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    curl \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    libffi-dev \
    make

WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/

# Create virtual environment
RUN uv venv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e .

# Runtime stage
FROM python:3.11-alpine AS runtime

# Install runtime dependencies
RUN apk add --no-cache \
    libffi \
    libstdc++ \
    curl

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure we use venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY ./app /app/app
COPY ./run.py /app/run.py

# Copy production environment configuration
COPY ./.env.example /app/.env

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use run.py as entry point
CMD ["python", "run.py"]
