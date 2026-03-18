# Multi-stage Dockerfile for Market Data Backend Platform
# Stage 1: Builder - Install dependencies
FROM python:3.14-slim AS builder

WORKDIR /build

# Install system dependencies (build-essential needed for chromadb native extensions)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies only (libgomp1 needed by onnxruntime/chromadb)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

# Set PYTHONPATH so the application module can be imported
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Create non-root user and ChromaDB data directory
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data/chromadb && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn market_data_backend_platform.main:app --host 0.0.0.0 --port 8000"]
