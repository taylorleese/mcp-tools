# Claude Context

Share contexts and todo lists between Claude Code sessions. Get ChatGPT's second opinion via OpenAI API. MCP server ready for future integration.

## Features

- **Context Management**: Save code, suggestions, errors, and conversations with ChatGPT's second opinion
- **Todo Persistence**: Never lose your todos when restarting - save and restore across sessions
- **Project-Based**: Automatic project path detection and organization
- **Full-Text Search**: Find contexts and todos by content, tags, or metadata
- **MCP Ready**: Built-in MCP server for future ChatGPT Desktop integration

## Quick Start

### Installation

```bash
# Navigate to project
cd claude-context

# Create and activate virtual environment
python3.13 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Configure API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

**Important:** Don't set `OPENAI_API_KEY` in your shell environment - it will override `.env`. If set, run `unset OPENAI_API_KEY`.

### Your First Commands

```bash
# Get ChatGPT's opinion on something
./claude-context context save-and-query \
  --type suggestion \
  --title "Redis caching strategy" \
  --content "Use Redis for session storage with 1-hour TTL" \
  --tags "caching,redis"

# Save your current todos
./claude-context todo save \
  --todos '[
    {"content":"Fix auth bug","status":"in_progress","activeForm":"Fixing auth bug"},
    {"content":"Write tests","status":"pending","activeForm":"Writing tests"}
  ]' \
  --context "Working on authentication"

# List everything
./claude-context context list
./claude-context todo list

# Restore todos later
./claude-context todo restore
```

## Command Reference

### Context Commands

```bash
# Save and query ChatGPT immediately
./claude-context context save-and-query \
  --type <type> \
  --title "Title" \
  --content "..." \
  --tags "tag1,tag2"

# Save without querying
./claude-context context save --type code --file path/to/file.py

# Ask ChatGPT about existing context
./claude-context context ask-chatgpt <context-id>

# Browse and search
./claude-context context list [--limit N] [--type TYPE]
./claude-context context search "query"
./claude-context context show <context-id>

# Delete
./claude-context context delete <context-id>
```

**Context Types:**
- `suggestion` - Architecture decisions, implementation plans
- `code` - Code snippets, implementations
- `conversation` - Discussions, Q&A sessions
- `error` - Error messages, stack traces, debugging

### Todo Commands

```bash
# Save current todos
./claude-context todo save \
  --todos '[{"content":"...","status":"pending","activeForm":"..."}]' \
  --context "What you're working on"

# Restore (defaults to active snapshot for current project)
./claude-context todo restore [<snapshot-id>]

# Browse and search
./claude-context todo list [--project-path PATH]
./claude-context todo search "query"
./claude-context todo show <snapshot-id>

# Delete
./claude-context todo delete <snapshot-id>
```

**Todo Status:** `pending`, `in_progress`, `completed`

### Get Help

```bash
./claude-context --help
./claude-context context --help
./claude-context todo --help
```

## Common Workflows

### Get a Second Opinion

When Claude suggests an implementation, get ChatGPT's perspective:

```bash
./claude-context context save-and-query \
  --type suggestion \
  --title "Microservices vs Monolith for e-commerce" \
  --content "Building platform with 5 services. Start microservices or monolith first?" \
  --tags "architecture,scalability"
```

ChatGPT's response appears immediately in your console.

### Debug with Two Perspectives

```bash
./claude-context context save-and-query \
  --type error \
  --title "CORS issue in production" \
  --content "Error: blocked by CORS policy. Headers: ..." \
  --tags "debugging,cors,production"
```

### Session Continuity

```bash
# End of work session
./claude-context todo save \
  --todos '[
    {"content":"Implement login","status":"completed","activeForm":"Implementing login"},
    {"content":"Add OAuth","status":"in_progress","activeForm":"Adding OAuth"},
    {"content":"Write tests","status":"pending","activeForm":"Writing tests"}
  ]' \
  --context "Day 2 of auth feature"

# Next session
./claude-context todo restore
```

### Share Across Claude Code Sessions

```bash
# Session 1: Save interesting discussions
./claude-context context save \
  --type conversation \
  --title "Performance optimization ideas" \
  --content "..." \
  --tags "performance"

# Session 2: Find and review
./claude-context context search "performance"
./claude-context context show <context-id>

# Or get ChatGPT's opinion
./claude-context context ask-chatgpt <context-id>
```

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                       # Your OpenAI API key

# Optional
CLAUDE_CONTEXT_DB_PATH=./data/contexts.db   # Database path (default shown)
CLAUDE_CONTEXT_MODEL=gpt-5                   # OpenAI model (default: gpt-5)
```

## Troubleshooting

### "Error 401: Invalid API key"
- Verify `OPENAI_API_KEY` is set in `.env`
- Check billing is enabled on your OpenAI account
- Run `unset OPENAI_API_KEY` to clear shell environment variable

### "No module named context_manager"
- Use `./claude-context` helper script (recommended)
- Or set `PYTHONPATH=src` before running Python directly

### Commands not found
- Activate venv: `source venv/bin/activate`
- Make script executable: `chmod +x claude-context`

### Todos not restoring
- Check you're in the same project directory
- Use `./claude-context todo list` to see all snapshots
- Restore specific snapshot: `./claude-context todo restore <snapshot-id>`

## Project Structure

```
claude-context/
├── src/
│   ├── mcp_server/          # MCP server (future integration)
│   │   └── server.py        # MCP tools and resources
│   ├── context_manager/     # CLI and storage
│   │   ├── cli.py          # Click-based CLI
│   │   ├── storage.py      # SQLite operations
│   │   └── openai_client.py # ChatGPT API client
│   └── models.py           # Pydantic data models
├── data/
│   └── contexts.db         # SQLite database
├── config/
│   └── mcp_config.json.example
├── requirements.txt
├── requirements-dev.txt
└── claude-context          # Helper script
```

## Future: MCP Integration

> **Note:** ChatGPT Desktop doesn't support MCP servers yet, but this project is ready!

The project includes a complete MCP server with these tools:

**Context Tools:**
- `context_search` - Search by query or tags
- `context_get` - Get by ID
- `context_list` - List recent
- `context_delete` - Delete by ID

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
3. **Be specific in content** - More detail = better ChatGPT responses
4. **Review ChatGPT suggestions** - They're helpful opinions, not rules
5. **Save todos regularly** - Build habit of saving at end of sessions

## License

MIT
