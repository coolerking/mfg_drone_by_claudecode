# Multi-stage Dockerfile for Production-Ready MCP Server
# Phase 6-3: Production Deployment

FROM python:3.11-slim-bullseye as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn==21.2.0 \
    psutil==5.9.6 \
    PyJWT==2.8.0 \
    prometheus-client==0.19.0 \
    cryptography==41.0.7

# Production stage
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
    ENABLE_MONITORING=true \
    ENABLE_AUDIT_LOGGING=true

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mcpserver && useradd -r -g mcpserver mcpserver

# Create application directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/config

# Set proper permissions
RUN chown -R mcpserver:mcpserver /app

# Switch to non-root user
USER mcpserver

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/mcp/system/health || exit 1

# Default command
CMD ["python", "start_phase5_mcp_server.py", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]