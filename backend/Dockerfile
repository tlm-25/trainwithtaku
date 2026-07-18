FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.17 /uv /uvx /bin/
RUN chmod +x /bin/uv /bin/uvx

# Copy project files first
COPY . /app

# Lock dependencies (optional if you already have uv.lock)
RUN uv lock

# Sync dependencies
RUN uv sync --locked

# Expose port
EXPOSE 8000

# Run app
CMD ["uv","run","uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]