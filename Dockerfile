FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install everything
RUN pip install --no-cache-dir mcp uvicorn starlette httpx pydantic pydantic-settings python-dotenv
RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# Use CMD instead of ENTRYPOINT so you can override it for debugging
CMD ["python", "-m", "ntnx_mcp.server"]
