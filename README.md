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
pip install -r requirements-dev.txt  # For development
# or
pip install -r requirements.txt  # For production only

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Usage from Claude Code

**Easy way** - Use the helper script:
```bash
# Get ChatGPT's opinion on something
./chatmcp save-and-query \
  --type suggestion \
  --title "Auth implementation plan" \
  --content "Your context here..."

# List saved contexts
./chatmcp list-contexts

# Search contexts
./chatmcp search "authentication"

# Show full context details
./chatmcp show <context-id>
```

**Manual way** - Direct Python module:
```bash
# IMPORTANT: Unset conflicting environment variables first
unset OPENAI_API_KEY

# Set PYTHONPATH
export PYTHONPATH=.

# Run commands
python -m src.context_manager save-and-query \
  --type suggestion \
  --title "Auth implementation plan" \
  --content "Your context here..."
```

**Available context types:**
- `conversation` - Conversation history
- `code` - Code snippets or files
- `suggestion` - Implementation plans or recommendations
- `error` - Error logs or debugging info

### 3. ChatGPT Desktop Integration

```bash
# Copy and customize the MCP config
cp config/mcp_config.json.example config/mcp_config.json
# Edit config/mcp_config.json and update the paths to your chatmcp directory
```

Add the contents of `config/mcp_config.json` to ChatGPT Desktop settings:
- Open ChatGPT Desktop
- Go to Settings → Integrations → Model Context Protocol
- Add the server configuration
- Restart ChatGPT Desktop

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
