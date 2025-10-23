# Claude Code ↔ ChatGPT Context Sharing

An MCP (Model Context Protocol) server that enables seamless context sharing between Claude Code and ChatGPT for getting second opinions and refining suggestions.

## Features

- **Console-First**: Get ChatGPT's opinions directly in Claude Code console
- **Context Storage**: Save conversations, code, suggestions, and errors
- **MCP Integration**: ChatGPT Desktop can query saved contexts via MCP
- **Automated Workflow**: Single command to save and get feedback

## Quick Start

### 1. Setup

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Usage from Claude Code

```bash
# Get ChatGPT's opinion on something
python -m context_manager save-and-query \
  --type suggestion \
  --title "Auth implementation plan" \
  --content "Your context here..."

# Just save without querying
python -m context_manager save \
  --type code \
  --title "New feature" \
  --file path/to/code.py

# List saved contexts
python -m context_manager list
```

### 3. ChatGPT Desktop Integration

Add to ChatGPT Desktop settings (Settings → Integrations → MCP):

```json
{
  "mcpServers": {
    "claude-context": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/Users/tleese/chatmcp",
      "env": {
        "PYTHONPATH": "/Users/tleese/chatmcp/src"
      }
    }
  }
}
```

Then ask ChatGPT: "What recent suggestions did Claude Code make?"

## Project Structure

```
chatmcp/
├── src/
│   ├── mcp_server/        # MCP server implementation
│   ├── context_manager/   # CLI and context management
│   └── models.py          # Data models
├── data/                  # SQLite database
├── config/                # Configuration files
├── requirements.txt
├── README.md
└── PLAN.md               # Detailed implementation plan
```

## Documentation

See [PLAN.md](./PLAN.md) for detailed architecture and implementation plan.

## License

MIT
