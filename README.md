# MCP Tools

Share contexts and todo lists between Claude Code sessions. Get second opinions from ChatGPT or Claude via API. MCP server ready for future integration.

## Features

- **Context Management**: Save code, suggestions, errors, and conversations with AI second opinions
- **AI Second Opinions**: Get feedback from both ChatGPT (OpenAI) and Claude (Anthropic)
- **Todo Persistence**: Never lose your todos when restarting - save and restore across sessions
- **Project-Based**: Automatic project path detection and organization
- **Full-Text Search**: Find contexts and todos by content, tags, or metadata
- **MCP Ready**: Built-in MCP server for future ChatGPT Desktop integration

## Quick Start

### Installation

```bash
# Navigate to project
cd mcp-tools

# Create and activate virtual environment
python3.13 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

**Important:** Don't set API keys in your shell environment - they will override `.env`. If set, run `unset OPENAI_API_KEY` or `unset ANTHROPIC_API_KEY`.

### Your First Commands

```bash
# Get ChatGPT's opinion on something
./mcp-tools context save-and-query \
  --type suggestion \
  --title "Redis caching strategy" \
  --content "Use Redis for session storage with 1-hour TTL" \
  --tags "caching,redis"

# Save your current todos
./mcp-tools todo save \
  --todos '[
    {"content":"Fix auth bug","status":"in_progress","activeForm":"Fixing auth bug"},
    {"content":"Write tests","status":"pending","activeForm":"Writing tests"}
  ]' \
  --context "Working on authentication"

# List everything
./mcp-tools context list
./mcp-tools todo list

# Restore todos later
./mcp-tools todo restore
```

## Command Reference

### Context Commands

```bash
# Save and query ChatGPT immediately
./mcp-tools context save-and-query \
  --type <type> \
  --title "Title" \
  --content "..." \
  --tags "tag1,tag2"

# Save without querying
./mcp-tools context save --type code --file path/to/file.py

# Ask ChatGPT or Claude about existing context
./mcp-tools context ask-chatgpt <context-id> [--question "Your question"]
./mcp-tools context ask-claude <context-id> [--question "Your question"]

# Browse and search
./mcp-tools context list [--limit N] [--type TYPE]
./mcp-tools context search "query"
./mcp-tools context show <context-id>

# Delete
./mcp-tools context delete <context-id>
```

**Context Types:**
- `suggestion` - Architecture decisions, implementation plans
- `code` - Code snippets, implementations
- `conversation` - Discussions, Q&A sessions
- `error` - Error messages, stack traces, debugging

### Todo Commands

```bash
# Save current todos
./mcp-tools todo save \
  --todos '[{"content":"...","status":"pending","activeForm":"..."}]' \
  --context "What you're working on"

# Restore (defaults to active snapshot for current project)
./mcp-tools todo restore [<snapshot-id>]

# Browse and search
./mcp-tools todo list [--project-path PATH]
./mcp-tools todo search "query"
./mcp-tools todo show <snapshot-id>

# Delete
./mcp-tools todo delete <snapshot-id>
```

**Todo Status:** `pending`, `in_progress`, `completed`

### Get Help

```bash
./mcp-tools --help
./mcp-tools context --help
./mcp-tools todo --help
```

## Common Workflows

### Get a Second Opinion

When Claude Code suggests an implementation, get another AI's perspective:

```bash
./mcp-tools context save-and-query \
  --type suggestion \
  --title "Microservices vs Monolith for e-commerce" \
  --content "Building platform with 5 services. Start microservices or monolith first?" \
  --tags "architecture,scalability"
```

The AI's response appears immediately in your console. You can also ask specific questions or get Claude's perspective:

```bash
# Ask a specific question about the context
./mcp-tools context ask-chatgpt <context-id> --question "What are the scalability concerns?"

# Get Claude's general opinion
./mcp-tools context ask-claude <context-id>

# Or ask Claude a specific question
./mcp-tools context ask-claude <context-id> --question "How would you handle database migrations?"
```

### Debug with Two Perspectives

```bash
./mcp-tools context save-and-query \
  --type error \
  --title "CORS issue in production" \
  --content "Error: blocked by CORS policy. Headers: ..." \
  --tags "debugging,cors,production"
```

### Session Continuity

```bash
# End of work session
./mcp-tools todo save \
  --todos '[
    {"content":"Implement login","status":"completed","activeForm":"Implementing login"},
    {"content":"Add OAuth","status":"in_progress","activeForm":"Adding OAuth"},
    {"content":"Write tests","status":"pending","activeForm":"Writing tests"}
  ]' \
  --context "Day 2 of auth feature"

# Next session
./mcp-tools todo restore
```

### Share Across Claude Code Sessions

```bash
# Session 1: Save interesting discussions
./mcp-tools context save \
  --type conversation \
  --title "Performance optimization ideas" \
  --content "..." \
  --tags "performance"

# Session 2: Find and review
./mcp-tools context search "performance"
./mcp-tools context show <context-id>

# Or ask AI specific questions
./mcp-tools context ask-chatgpt <context-id> --question "What's the performance impact?"
./mcp-tools context ask-claude <context-id> --question "Are there any security concerns?"
```

## Environment Variables

```bash
# Required (at least one for AI features)
OPENAI_API_KEY=sk-...                           # Your OpenAI API key
ANTHROPIC_API_KEY=sk-ant-...                    # Your Anthropic API key

# Optional
MCP_TOOLS_DB_PATH=./data/contexts.db            # Database path (default shown)
MCP_TOOLS_MODEL=gpt-5                           # OpenAI model (default: gpt-5)
MCP_TOOLS_CLAUDE_MODEL=claude-sonnet-4-5-20250929  # Claude model
```

## Troubleshooting

### "Error 401: Invalid API key"
- Verify API keys are set in `.env` (OPENAI_API_KEY and/or ANTHROPIC_API_KEY)
- Check billing is enabled on your OpenAI/Anthropic account
- Run `unset OPENAI_API_KEY` or `unset ANTHROPIC_API_KEY` to clear shell environment variables

### "No module named context_manager"
- Use `./mcp-tools` helper script (recommended)
- Or set `PYTHONPATH=src` before running Python directly

### Commands not found
- Activate venv: `source venv/bin/activate`
- Make script executable: `chmod +x mcp-tools`

### Todos not restoring
- Check you're in the same project directory
- Use `./mcp-tools todo list` to see all snapshots
- Restore specific snapshot: `./mcp-tools todo restore <snapshot-id>`

## Project Structure

```
mcp-tools/
├── src/
│   ├── mcp_server/          # MCP server (future integration)
│   │   └── server.py        # MCP tools and resources
│   ├── context_manager/     # CLI and storage
│   │   ├── cli.py          # Click-based CLI
│   │   ├── storage.py      # SQLite operations
│   │   ├── openai_client.py # ChatGPT API client
│   │   └── anthropic_client.py # Claude API client
│   └── models.py           # Pydantic data models
├── data/
│   └── contexts.db         # SQLite database
├── config/
│   └── mcp_config.json.example
├── requirements.txt
├── requirements-dev.txt
└── mcp-tools          # Helper script
```

## Future: MCP Integration

> **Note:** ChatGPT Desktop doesn't support MCP servers yet, but this project is ready!

The project includes a complete MCP server with these tools:

**Context Tools:**
- `context_search` - Search by query or tags
- `context_get` - Get by ID
- `context_list` - List recent
- `context_delete` - Delete by ID

**AI Opinion Tools:**
- `ask_chatgpt` - Ask ChatGPT about a context (supports custom questions)
- `ask_claude` - Ask Claude about a context (supports custom questions)

**Todo Tools:**
- `todo_search` - Search snapshots
- `todo_get` - Get by ID
- `todo_list` - List recent
- `todo_save` - Save snapshot
- `todo_restore` - Get active/specific snapshot
- `todo_delete` - Delete by ID

Once MCP clients add support, you'll be able to query: "What did Claude Code save about authentication?" or "Show my active todos" from ChatGPT Desktop.

## Development

### Running Tests
```bash
source venv/bin/activate
pytest
```

### Code Quality
```bash
# Run all checks
pre-commit run --all-files

# Individual tools
black .
ruff check .
mypy src/
```

## Tips

1. **Use descriptive titles** - Makes searching easier later
2. **Add relevant tags** - Helps organize and find contexts
3. **Be specific in content** - More detail = better AI responses
4. **Compare AI opinions** - Get both ChatGPT and Claude perspectives on important decisions
5. **Review AI suggestions** - They're helpful opinions, not rules
6. **Save todos regularly** - Build habit of saving at end of sessions

## License

MIT
