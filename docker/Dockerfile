# Multi-stage Docker build for Dolibarr MCP Server
# Version 2.1.0 - TOON format + DragonflyDB cache support
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies (including redis for cache)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir redis>=5.0.0

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/
COPY README.md LICENSE ./

# Install the package with cache extras
RUN pip install -e ".[cache]"

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r dolibarr && useradd -r -g dolibarr dolibarr

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/src/ /app/src/

# Create working directory and set ownership
WORKDIR /app
RUN chown -R dolibarr:dolibarr /app

# Switch to non-root user
USER dolibarr

# Health check via HTTP endpoint (no auth required)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port (for future HTTP interface)
EXPOSE 8080

# Default command runs the MCP server
CMD ["python", "-m", "dolibarr_mcp.dolibarr_mcp_server"]

# Labels for metadata
LABEL org.opencontainers.image.title="Dolibarr MCP Server" \
      org.opencontainers.image.description="AI-optimized MCP server for Dolibarr ERP with TOON format and DragonflyDB cache" \
      org.opencontainers.image.url="https://github.com/latinogino/dolibarr-mcp" \
      org.opencontainers.image.source="https://github.com/latinogino/dolibarr-mcp" \
      org.opencontainers.image.version="2.1.0" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.features="TOON format, DragonflyDB cache, 60% token reduction"
