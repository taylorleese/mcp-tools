# Build stage
FROM python:3.14-slim-bookworm@sha256:e8ea0e4fc6f1876e7d2cfccc0071847534b1d72f2359cf0fd494006d05358faa AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml README.md LICENSE ./
COPY requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir pip==25.3 \
        --hash sha256:8d0538dbbd7babbd207f261ed969c65de439f6bc9e5dbd3b3b9a77f25d95f343 \
        --hash sha256:9655943313a94722b7774661c21049070f6bbb0a1516bf02f7c8d5d9201514cd && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src

# Install the project (non-editable for production)
RUN /app/.venv/bin/pip install --no-cache-dir .

# Runtime stage
FROM python:3.14-slim-bookworm@sha256:e8ea0e4fc6f1876e7d2cfccc0071847534b1d72f2359cf0fd494006d05358faa

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

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
