# Python Backend Starter

A FastAPI-based Python backend starter template with Docker support and modern Python tooling.

## Features

- [FastAPI](https://fastapi.tiangolo.com/) for high-performance API development
- [UV](https://github.com/astral-sh/uv) for fast Python package management
- Docker and Docker Compose support
- Pytest for testing
- Ruff for linting and formatting

## Requirements

- Python >= 3.10
- UV package manager
- Docker (optional, for containerization)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   uv venv
   uv pip install -e ".[dev]"
   ```

## Running the server

```bash
make run 
```