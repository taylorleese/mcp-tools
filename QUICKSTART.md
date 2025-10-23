# Claude Context - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.13+
- OpenAI API key (for ChatGPT integration)
- ChatGPT Desktop (optional, for MCP integration)

## Installation

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

**Important:** Don't set `OPENAI_API_KEY` in your shell environment, as it will override `.env`. If you have it set, run `unset OPENAI_API_KEY`.

## Basic Commands

### Context Management

```bash
# Save and get ChatGPT's opinion immediately
./claude-context context save-and-query \
  --type suggestion \
  --title "Redis caching strategy" \
  --content "Use Redis for session storage with 1-hour TTL" \
  --tags "caching,redis"

# Save without querying
./claude-context context save \
  --type code \
  --title "Auth middleware" \
  --file src/auth.py

# List all contexts
./claude-context context list

# Search
./claude-context context search "redis"

# Show details
./claude-context context show <context-id>

# Ask ChatGPT about existing context
./claude-context context ask-chatgpt <context-id>

# Delete
./claude-context context delete <context-id>
```

### Todo Management

```bash
# Save current todos
./claude-context todo save \
  --todos '[
    {"content":"Fix auth bug","status":"in_progress","activeForm":"Fixing auth bug"},
    {"content":"Write tests","status":"pending","activeForm":"Writing tests"}
  ]' \
  --context "Working on authentication"

# Restore (active snapshot for current project)
./claude-context todo restore

# List all snapshots
./claude-context todo list

# Search
./claude-context todo search "auth"

# Show details
./claude-context todo show <snapshot-id>

# Delete
./claude-context todo delete <snapshot-id>
```

## Context Types

Choose the right type for your use case:

- **`suggestion`** - Architecture decisions, implementation plans, approaches
- **`code`** - Code snippets, implementations, file contents
- **`conversation`** - Discussions, Q&A sessions
- **`error`** - Error messages, stack traces, debugging info

## Examples

### Get a Second Opinion

```bash
./claude-context context save-and-query \
  --type suggestion \
  --title "Microservices vs Monolith" \
  --content "Building e-commerce with 5 services. Start microservices or monolith?" \
  --tags "architecture,scalability"
```

Output shows ChatGPT's response immediately in your console.

### Review Code

```bash
./claude-context context save-and-query \
  --type code \
  --title "User auth middleware" \
  --file src/middleware/auth.ts \
  --tags "security,typescript"
```

### Debug an Error

```bash
./claude-context context save-and-query \
  --type error \
  --title "Database timeout in production" \
  --content "Error: connection timeout after 30s during peak hours..." \
  --tags "database,production"
```

### Save Todo Progress

```bash
# End of day
./claude-context todo save \
  --todos '[
    {"content":"Implement login","status":"completed","activeForm":"Implementing login"},
    {"content":"Add OAuth","status":"in_progress","activeForm":"Adding OAuth"},
    {"content":"Write integration tests","status":"pending","activeForm":"Writing integration tests"}
  ]' \
  --context "Day 2 of auth feature"

# Next morning
./claude-context todo restore
```

## ChatGPT Desktop Integration (Optional)

### Setup

1. **Create MCP config**:
   ```bash
   cp config/mcp_config.json.example config/mcp_config.json
   ```

2. **Edit `config/mcp_config.json`** - Update paths to your `claude-context` directory (use absolute paths).

3. **Add to ChatGPT Desktop**:
   - Open ChatGPT Desktop
   - Settings → Integrations → Model Context Protocol
   - Add the server configuration
   - Restart ChatGPT Desktop

4. **Verify**:
   - In ChatGPT Desktop, check `/mcp` command
   - You should see `claude-context` server with tools

### Using ChatGPT with Your Contexts

Once configured, ask ChatGPT:

```
"What recent suggestions did Claude Code make about authentication?"
"Search my contexts for Redis"
"Show me my active todo list"
"What errors have I saved recently?"
```

ChatGPT will use MCP tools to access your data.

### Available MCP Tools

**Context:**
- `context_search` - Search by query or tags
- `context_get` - Get by ID
- `context_list` - List recent
- `context_delete` - Delete by ID

**Todo:**
- `todo_search` - Search snapshots
- `todo_get` - Get snapshot by ID
- `todo_list` - List recent snapshots
- `todo_save` - Save new snapshot
- `todo_restore` - Get active/specific snapshot
- `todo_delete` - Delete snapshot

## Workflows

### Real-Time Second Opinion

1. Working on a design in Claude Code
2. Run `./claude-context context save-and-query`
3. Get ChatGPT's opinion immediately
4. Consider both perspectives
5. Make decision

### Session Continuity

1. End of session: `./claude-context todo save --todos '[...]'`
2. Start new session: `./claude-context todo restore`
3. Continue where you left off

### Team Collaboration

1. Save architectural decisions as contexts
2. Share database or context IDs with team
3. Everyone can query same contexts
4. Consistent second opinions across team

## Tips

1. **Descriptive titles** - Makes searching easier
2. **Relevant tags** - Helps categorize and find
3. **Specific content** - Better context = better ChatGPT responses
4. **Review responses** - ChatGPT suggestions are opinions, not rules
5. **Track iterations** - Reference previous context IDs in new ones

## Troubleshooting

### "Error 401: Invalid API key"
- Check `.env` has `OPENAI_API_KEY=sk-...`
- Verify billing is set up on OpenAI account
- Run `unset OPENAI_API_KEY` in shell

### "No module named context_manager"
- Use `./claude-context` helper script
- Or set `PYTHONPATH=src` before running Python directly

### ChatGPT Desktop can't connect
- Use absolute paths in `config/mcp_config.json`
- Restart ChatGPT Desktop after config changes
- Verify venv is activated and dependencies installed
- Check MCP server logs in ChatGPT Desktop

### Commands not found
- Make sure you activated the venv: `source venv/bin/activate`
- Make helper script executable: `chmod +x claude-context`

## Command Reference

### Context Commands
```bash
./claude-context context save [options]
./claude-context context save-and-query [options]
./claude-context context ask-chatgpt <id>
./claude-context context list [--limit N] [--type TYPE]
./claude-context context search <query>
./claude-context context show <id>
./claude-context context delete <id>
```

### Todo Commands
```bash
./claude-context todo save --todos JSON [options]
./claude-context todo restore [<id>]
./claude-context todo list [--project-path PATH]
./claude-context todo search <query>
./claude-context todo show <id>
./claude-context todo delete <id>
```

### Get Help
```bash
./claude-context --help
./claude-context context --help
./claude-context todo --help
```

## Next Steps

- Read [README.md](./README.md) for complete documentation
- Explore all command options with `--help`
- Customize OpenAI prompts in `src/context_manager/openai_client.py`
- Check `/mcp` in Claude Code to see MCP tool details

Happy context sharing! 🚀
