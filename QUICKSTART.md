# ChatMCP Quick Start Guide

Get up and running with Claude Code ↔ ChatGPT context sharing in 5 minutes!

## Prerequisites

- Python 3.13+
- OpenAI API key with billing enabled
- ChatGPT Desktop (optional, for MCP integration)

## Setup

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-proj-your-key-here
```

**Important:** Make sure you don't have `OPENAI_API_KEY` set in your shell environment, as it will override the `.env` file. If you do, run `unset OPENAI_API_KEY` first.

## Basic Usage

### Save and Get ChatGPT Opinion

```bash
./chatmcp save-and-query \
  --type suggestion \
  --title "Redis caching strategy" \
  --content "Planning to use Redis for session storage with 1-hour TTL" \
  --tags "caching,redis,performance"
```

### List All Saved Contexts

```bash
./chatmcp list-contexts
```

Output shows:
- ✓ = Has ChatGPT response
- ○ = No ChatGPT response yet

### Search for Contexts

```bash
./chatmcp search "redis"
./chatmcp search "authentication"
```

### View Full Context Details

```bash
./chatmcp show <context-id>
```

This shows:
- Original context
- All metadata and tags
- ChatGPT's response (if available)

### Query ChatGPT About Existing Context

```bash
# If you saved without querying, you can query later
./chatmcp query <context-id>
```

## Context Types

Choose the appropriate type for your context:

- **suggestion** - Implementation plans, architecture decisions, approaches
- **code** - Code snippets, implementations, file contents
- **conversation** - Discussion threads, Q&A sessions
- **error** - Error messages, stack traces, debugging info

## Examples

### Example 1: Get Opinion on Architecture

```bash
./chatmcp save-and-query \
  --type suggestion \
  --title "Microservices vs Monolith for e-commerce platform" \
  --content "We're building an e-commerce platform with 5 core services. Should we go microservices from day 1 or start with a monolith?" \
  --tags "architecture,scalability"
```

### Example 2: Review Code

```bash
./chatmcp save-and-query \
  --type code \
  --title "User authentication middleware" \
  --file src/middleware/auth.ts \
  --tags "security,typescript"
```

### Example 3: Debug Error

```bash
./chatmcp save-and-query \
  --type error \
  --title "Database connection timeout" \
  --content "Getting 'connection timeout after 30s' errors during peak hours. Stack trace: ..." \
  --tags "database,debugging,production"
```

## ChatGPT Desktop Integration (Optional)

### Setup MCP Server

1. Copy and customize config:
```bash
cp config/mcp_config.json.example config/mcp_config.json
# Edit config/mcp_config.json and update paths to your chatmcp directory
```

2. Add to ChatGPT Desktop:
   - Open ChatGPT Desktop
   - Go to Settings → Integrations → Model Context Protocol
   - Add the contents of `config/mcp_config.json`
   - Restart ChatGPT Desktop

3. Test in ChatGPT:
   - "What recent suggestions did Claude Code make?"
   - "Search my Claude contexts for authentication"
   - "Show me the details of context ID abc-123"

### Available MCP Tools

ChatGPT can use these tools to query your contexts:

- `search_context` - Full-text search
- `get_context_details` - Get specific context by ID
- `list_recent_contexts` - Browse recent contexts
- `get_contexts_by_tags` - Find by tags

### Available MCP Resources

ChatGPT can browse:

- `claude-context://recent` - Last 20 contexts
- `claude-context://types/conversation` - All conversations
- `claude-context://types/code` - All code contexts
- `claude-context://types/suggestion` - All suggestions
- `claude-context://types/error` - All error contexts

## Workflows

### Workflow 1: Real-time Second Opinion

1. Working in Claude Code on a design decision
2. Run `./chatmcp save-and-query` with the context
3. Get ChatGPT's opinion immediately in console
4. Consider both perspectives
5. Make informed decision

### Workflow 2: Later Review

1. Save interesting discussions: `./chatmcp save ...`
2. Later, open ChatGPT Desktop
3. Ask: "Review my recent Claude Code contexts about authentication"
4. ChatGPT uses MCP to access and analyze them
5. Get broader perspective on accumulated decisions

### Workflow 3: Team Collaboration

1. Save important architectural decisions
2. Export database or share context IDs
3. Team members can query same contexts
4. Everyone gets consistent second opinions

## Tips

1. **Use descriptive titles** - Makes searching easier later
2. **Add relevant tags** - Helps categorize and find contexts
3. **Be specific in content** - More context = better ChatGPT responses
4. **Review responses** - ChatGPT's suggestions are opinions, not gospel
5. **Track iterations** - Save follow-up contexts referencing original IDs

## Troubleshooting

### "Error 401: Invalid API key"

- Make sure your OpenAI API key is in `.env`
- Verify billing is set up on your OpenAI account
- Run `unset OPENAI_API_KEY` to clear shell environment variable

### "No module named context_manager"

- Use the `./chatmcp` helper script instead of calling Python directly
- Or set `PYTHONPATH=.` before running

### ChatGPT Desktop can't connect

- Verify paths in `config/mcp_config.json` are absolute paths
- Restart ChatGPT Desktop after adding the config
- Check that venv is activated and dependencies installed

## Next Steps

- Check [PLAN.md](./PLAN.md) for detailed architecture
- See [README.md](./README.md) for complete documentation
- Customize prompts in `src/context_manager/openai_client.py`
- Add more sophisticated search/tagging logic

Happy context sharing! 🚀
