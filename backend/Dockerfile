
FROM python:3.12-slim

WORKDIR /app

#install uv
COPY --from=ghcr.io/astral-sh/uv:0.8.19 /uv /uvx /bin/


RUN uv sync --locked 

COPY . /app

EXPOSE 8000

CMD ["uv","run","uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]