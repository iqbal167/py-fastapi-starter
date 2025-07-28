.PHONY: run compose test

run:
	@uv run uvicorn app.main:app --reload

compose:
	@docker compose up --build -d

test:
	@uv run pytest

lint:
	@uv run ruff check . --fix

format:
	@uv run ruff format .
