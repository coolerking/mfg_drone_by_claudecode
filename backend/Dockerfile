# Multi-stage Dockerfile for MFG Drone Backend API
# Phase 5: Production-ready containerization

# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HOST=0.0.0.0 \
    PORT=8000 \
    LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory and data directories
WORKDIR /app
RUN mkdir -p /app/data/datasets /app/data/models /app/data/logs \
    && chown -R appuser:appuser /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting MFG Drone Backend API Server..."\n\
echo "Environment: ${ENVIRONMENT:-development}"\n\
echo "Host: ${HOST}"\n\
echo "Port: ${PORT}"\n\
echo "Log Level: ${LOG_LEVEL}"\n\
\n\
# Run database migrations or initialization if needed\n\
# python -m api_server.scripts.init_db\n\
\n\
# Start the server\n\
exec python -m uvicorn api_server.main:app \\\n\
    --host ${HOST} \\\n\
    --port ${PORT} \\\n\
    --log-level ${LOG_LEVEL} \\\n\
    --access-log \\\n\
    --loop uvloop \\\n\
    --http httptools\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to non-root user
USER appuser

# Set PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Default command
CMD ["/app/start.sh"]

# Labels for metadata
LABEL maintainer="MFG Drone Project" \
      version="5.0.0" \
      description="MFG Drone Backend API Server with Web Dashboard" \
      phase="Phase 5 - Production Ready"