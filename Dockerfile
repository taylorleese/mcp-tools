# Build stage
FROM python:3.14-slim-bookworm@sha256:d13fa0424035d290decef3d575cea23d1b7d5952cdf429df8f5542c71e961576 AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml README.md LICENSE ./
COPY requirements-pip.txt requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --require-hashes --no-cache-dir -r requirements-pip.txt && \
    /app/.venv/bin/pip install --require-hashes --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src

# Runtime stage
FROM python:3.14-slim-bookworm@sha256:d13fa0424035d290decef3d575cea23d1b7d5952cdf429df8f5542c71e961576

WORKDIR /app

# Copy the virtual environment and source code from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Add source to PYTHONPATH so modules can be found without installation
ENV PYTHONPATH="/app/src"

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Run as non-root user for security
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

# Create directory for database with proper permissions
RUN mkdir -p /home/app/.mcp-toolz

# Set default database path
ENV MCP_TOOLZ_DB_PATH=/home/app/.mcp-toolz/contexts.db

# Health check - verify the MCP server process is running
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD pgrep -f "python -m mcp_server" > /dev/null || exit 1

# Run the MCP server
ENTRYPOINT ["python", "-m", "mcp_server"]
