FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir mcp httpx pydantic pydantic-settings python-dotenv uvicorn
RUN pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "src.ntnx_mcp.server:app", "--host", "0.0.0.0", "--port", "8080"]
