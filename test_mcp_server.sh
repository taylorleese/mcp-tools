#!/bin/bash
cd /Users/tleese/chatmcp
export PYTHONPATH=/Users/tleese/chatmcp

echo "Testing MCP server startup..."
echo "================================"

# Run the server and capture output
/Users/tleese/chatmcp/venv/bin/python -m src.mcp_server 2>&1 | head -20 &
SERVER_PID=$!

sleep 2

# Check if still running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✓ Server is running (PID: $SERVER_PID)"
    kill $SERVER_PID
else
    echo "✗ Server exited"
fi

wait $SERVER_PID 2>/dev/null
