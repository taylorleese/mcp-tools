# MCP Toolz

[![CI](https://github.com/taylorleese/mcp-toolz/actions/workflows/ci.yml/badge.svg)](https://github.com/taylorleese/mcp-toolz/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/taylorleese/mcp-toolz/branch/main/graph/badge.svg)](https://codecov.io/gh/taylorleese/mcp-toolz)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

MCP server for Claude Code providing context management, todo persistence, and AI second opinions. Share contexts and todos across sessions, get feedback from ChatGPT or Claude, and access everything via MCP tools.

## Features

- **🔌 MCP Server**: Works NOW with Claude Code - full tool integration ready
- **Session Continuity**: Never lose context when restarting Claude Code - restore "what was I working on last session"
- **Project Organization**: Contexts and todos automatically organized by project directory
- **Session Tracking**: Every Claude Code session gets a unique ID - track your work over time
- **AI Second Opinions**: Get feedback from both ChatGPT (OpenAI) and Claude (Anthropic) on your code and decisions
- **Context Types**: Save conversations, code snippets, architectural suggestions, or error traces
- **Persistent Todos**: Save and restore your todo list across sessions - never forget where you left off
- **Full-Text Search**: Find anything by content, tags, project, or session
- **CLI + MCP**: Use via Claude Code MCP tools or standalone CLI commands

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

**Note:** The `./mcp-tools` wrapper automatically uses `.env` and ignores shell environment variables.

### MCP Server Setup (Recommended)

The primary way to use mcp-toolz is via the MCP server in Claude Code:

1. **Add to Claude Code settings** (add this JSON to your Claude Code MCP settings):

```json
{
  "mcpServers": {
    "mcp-toolz": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/absolute/path/to/mcp-tools",
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-tools/src"
      }
    }
  }
}
```

2. **Update the path** in the config above with your actual installation path

3. **Configure API keys** in `.env` file (API keys are read from `.env`, not from MCP config)

4. **Restart Claude Code** to load the MCP server

5. **Use MCP tools in Claude Code**:
   - "Save this context about authentication"
   - "Ask ChatGPT about the last context I saved"
   - "Show my active todos"
   - "Search contexts tagged with 'bug'"

All MCP tools are automatically available - see [MCP Server Tools](#mcp-server-tools) below.

## MCP Server Tools

The MCP server works NOW with Claude Code and provides these tools:

**Context Tools:**
- `context_save` - Save a new context (automatically includes session info)
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

**Session Tracking:**
When saving contexts through MCP tools, they are automatically tagged with:
- Current project directory (`project_path`)
- Session ID (unique per Claude Code session)
- Session timestamp (when the session started)

**Future:** Once ChatGPT Desktop adds MCP support, you'll be able to use these same tools there too.

## Usage Examples

Here are practical examples of how to use mcp-toolz in Claude Code:

### Example 1: Get a Second Opinion on Architecture Decisions

**Prompt:**
```
I'm deciding between using Redis or Memcached for caching user sessions.
Save this as a context and ask ChatGPT for a second opinion.
Use tags: caching, redis, memcached, architecture
```

**What happens:**
1. Claude Code uses `context_save` to save your architectural decision
2. Then uses `ask_chatgpt` to get ChatGPT's perspective
3. You get both AI opinions to inform your decision

**Follow-up prompts:**
- "Ask Claude the same question for comparison"
- "Search my contexts tagged with 'architecture'"

### Example 2: Session Continuity - Never Lose Your Place

**Prompt (end of work session):**
```
Save my current todo list so I can restore it tomorrow
```

**What happens:**
1. Claude Code uses `todo_save` to snapshot your current work state
2. Todos are saved with project path and timestamp

**Next day prompt:**
```
What was I working on yesterday? Restore my todos.
```

**What happens:**
1. Claude Code uses `todo_restore` to get your last snapshot
2. Shows you exactly where you left off
3. You can jump right back into work

### Example 3: Debug with Multiple AI Perspectives

**Prompt:**
```
I'm getting "TypeError: Cannot read property 'map' of undefined" in my React component.
The error occurs in UserList.jsx when rendering the users array.
Save this as an error context and ask both ChatGPT and Claude for debugging suggestions.
Tags: react, debugging, javascript
```

**What happens:**
1. Claude Code uses `context_save` to record the error
2. Uses `ask_chatgpt` to get OpenAI's debugging approach
3. Uses `ask_claude` to get Anthropic's perspective
4. You see two different debugging strategies

**Follow-up prompts:**
- "Search for other contexts tagged with 'react' bugs"
- "Show me contexts from my last session"

### Example 4: Track Performance Optimization Ideas

**Prompt:**
```
Save this performance optimization idea: "Lazy load images below the fold using
Intersection Observer API. Estimated 40% reduction in initial page load."
Type: suggestion, Tags: performance, optimization, images
```

**What happens:**
1. Claude Code uses `context_save` with type "suggestion"
2. Context is searchable and tied to current project
3. Available across all future sessions

**Later prompt:**
```
Search my contexts for performance optimization ideas
```

**What happens:**
1. Claude Code uses `context_search` with your query
2. Returns all matching contexts across sessions
3. You can review past optimization ideas

### Example 5: Cross-Session Knowledge Sharing

**Prompt (in Project A):**
```
I figured out how to handle OAuth refresh tokens properly.
Save this so I can reference it in other projects:
"Store refresh tokens in httpOnly cookies, access tokens in memory only.
Rotate refresh tokens on each use. Set 7-day expiry on refresh, 15min on access."
Type: code, Tags: oauth, security, authentication
```

**Prompt (later in Project B):**
```
How did I implement OAuth refresh tokens in my last project?
Search for contexts about oauth and show me what I saved.
```

**What happens:**
1. Claude Code uses `context_search` to find your OAuth implementation
2. Retrieves the context across projects
3. You reuse your own knowledge without starting from scratch

## Sharing Contexts Between Agents

mcp-toolz makes it easy to share contexts and todos across multiple Claude Code sessions or agents.

### MCP Resources (Passive Discovery)

Claude Code can automatically discover and read contexts/todos via MCP resources:

**Context Resources:**
- `mcp-toolz://contexts/project/recent` - Recent contexts for current project
- `mcp-toolz://contexts/project/sessions` - List of recent Claude Code sessions for current project
- `mcp-toolz://contexts/session/{session_id}` - All contexts from a specific session

**Todo Resources:**
- `mcp-toolz://todos/recent` - Last 20 todo snapshots (all projects)
- `mcp-toolz://todos/active` - Active todos for current working directory

**Session Tracking:**
Each Claude Code session automatically gets a unique session ID. All contexts saved during that session are tagged with:
- `session_id` - UUID of the Claude Code session
- `session_timestamp` - When the session started
- `project_path` - Directory where the context was created

This makes it easy to restore context from previous sessions: "Show me what I was working on in my last session"

Resources are read-only views into the shared database. Claude Code can discover them automatically without explicit tool calls.

### Shared Database Setup

**By default**, mcp-toolz stores all data in `~/.mcp-toolz/contexts.db`, which is automatically shared across all projects on the same machine. No additional configuration needed!

**For advanced use cases** (syncing across multiple machines via Dropbox, iCloud, etc.):

1. **Choose a synced location** for the database:
```bash
# Example: Use a synced folder (Dropbox, iCloud, network drive)
mkdir -p ~/Dropbox/mcp-toolz-shared
```

2. **Update `.env` file** or MCP config to point to the synced database:
```bash
# In .env file
MCP_TOOLS_DB_PATH=~/Dropbox/mcp-toolz-shared/contexts.db
```

Or in your MCP config:
```json
{
  "mcpServers": {
    "mcp-toolz": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/absolute/path/to/mcp-tools",
      "env": {
        "PYTHONPATH": "/absolute/path/to/mcp-tools/src",
        "MCP_TOOLS_DB_PATH": "/Users/you/Dropbox/mcp-toolz-shared/contexts.db"
      }
    }
  }
}
```

3. **Restart Claude Code** - it now uses the synced database location

### How It Works

- **Contexts**: Organized by `project_path` (each directory gets its own contexts)
- **Session Tracking**: Contexts tagged with session ID and timestamp for easy restoration
- **Todos**: Organized by `project_path` (each directory gets its own snapshots)
- **Single SQLite DB**: All data stored in one database, filtered by project and session
- **Automatic Updates**: Changes made in one session are immediately visible to others

### Use Cases

- **Multiple machines**: Keep contexts in sync across laptop and desktop
- **Session continuity**: Pick up where you left off after restarting Claude Code

## CLI Usage (Alternative)

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
OPENAI_API_KEY=sk-...                              # Your OpenAI API key
ANTHROPIC_API_KEY=sk-ant-...                       # Your Anthropic API key

# Optional
MCP_TOOLS_DB_PATH=~/.mcp-toolz/contexts.db         # Shared database location (default)
MCP_TOOLS_MODEL=gpt-5                              # OpenAI model (default: gpt-5)
MCP_TOOLS_CLAUDE_MODEL=claude-sonnet-4-5-20250929  # Claude model
```

## Troubleshooting

### "Error 401: Invalid API key"
- Verify API keys are set in `.env` (OPENAI_API_KEY and/or ANTHROPIC_API_KEY)
- Check billing is enabled on your OpenAI/Anthropic account
- The `./mcp-tools` wrapper automatically unsets shell environment variables to use `.env`

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
mcp-toolz/
├── src/
│   ├── mcp_server/          # MCP server for Claude Code
│   │   └── server.py        # MCP tools and resources
│   ├── context_manager/     # CLI and storage
│   │   ├── cli.py          # Click-based CLI
│   │   ├── storage.py      # SQLite operations
│   │   ├── openai_client.py # ChatGPT API client
│   │   └── anthropic_client.py # Claude API client
│   └── models.py           # Pydantic data models
├── data/
│   └── contexts.db         # SQLite database
├── requirements.txt
├── requirements-dev.txt
└── mcp-tools               # Helper script
```

## Development

### Setup for Contributors

```bash
# Clone and install
git clone https://github.com/taylorleese/mcp-toolz.git
cd mcp-tools
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# Install pre-commit hooks (IMPORTANT!)
pre-commit install

# Copy and configure .env
cp .env.example .env
# Edit .env with your API keys
```

### Running Tests
```bash
source venv/bin/activate
pytest
```

### Code Quality
```bash
# Run all checks (runs automatically on commit after pre-commit install)
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
