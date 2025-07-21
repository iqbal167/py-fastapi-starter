# Builder
FROM python:3.11-alpine AS builder

RUN apk add --no-cache curl gcc musl-dev libffi-dev

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/

RUN uv venv

COPY pyproject.toml uv.lock ./

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


# Runtime
FROM python:3.11-alpine AS runtime

WORKDIR /app

RUN apk add --no-cache libffi

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
