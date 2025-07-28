# Builder
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

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/

RUN uv venv

COPY pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e .


# Runtime
FROM python:3.11-alpine AS runtime

# Install runtime dependencies
RUN apk add --no-cache \
    libffi \
    libstdc++

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
