FROM python:3.13-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY server.py .
COPY ntnx_mcp/ ./ntnx_mcp/

EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Command to execute your server on startup
CMD ["python", "server.py"]
