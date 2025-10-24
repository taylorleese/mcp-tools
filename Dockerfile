# Build stage
FROM python:3.14-slim-bookworm AS builder

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
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src

# Install the project (non-editable for production)
RUN /app/.venv/bin/pip install --no-cache-dir .

# Runtime stage
FROM python:3.14-slim-bookworm

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

# Run the MCP server
ENTRYPOINT ["python", "-m", "mcp_server"]
