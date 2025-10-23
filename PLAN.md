# Claude Code ↔ ChatGPT Context Sharing - MCP Server

## Overview

An MCP server that enables seamless context sharing between Claude Code and ChatGPT for getting second opinions and refining suggestions - all from within the Claude Code console interface.

## Architecture

### Core Components

1. **MCP Server** (Python)
   - Exposes saved contexts as Resources and Tools
   - ChatGPT Desktop connects to this server
   - Stores context in local SQLite database

2. **Context Manager** (Python CLI/Module)
   - Invoked by Claude Code via Bash commands
   - Saves context to the MCP server's database
   - Calls OpenAI API to get ChatGPT's opinion automatically
   - Returns suggestions directly to Claude Code console

3. **Workflow**
   ```
   User in Claude Code: "Get a second opinion from ChatGPT on this auth plan"
   ↓
   Claude Code invokes: `python context_manager.py save-and-query "auth plan" --context "..."`
   ↓
   Script saves context to database (available via MCP for later)
   ↓
   Script calls OpenAI API with context
   ↓
   ChatGPT's response printed to Claude Code console
   ```

### Data Model

```python
ContextEntry {
    id: str                    # UUID
    timestamp: datetime        # When saved
    type: str                  # "conversation" | "code" | "suggestion" | "error"
    title: str                 # Brief description
    content: dict {            # Flexible content structure
        messages?: list        # Conversation history
        code?: dict            # Code snippets with file paths
        suggestions?: str      # Plans/recommendations
        errors?: str           # Error logs/stack traces
    }
    tags: list[str]           # Searchable keywords
    metadata: dict            # Project name, files, etc.
    chatgpt_response?: str    # If queried, store the response
}
```

## Implementation Plan

### Phase 1: Environment & Project Setup

- [x] Create Python virtual environment
- [ ] Install dependencies:
  - `mcp` - Official Python MCP SDK
  - `pydantic` - Schema validation
  - `openai` - OpenAI API client
  - `click` - CLI framework
  - `sqlite3` - Built-in, for storage
- [ ] Create project structure:
  ```
  chatmcp/
  ├── venv/
  ├── src/
  │   ├── mcp_server/
  │   │   ├── __init__.py
  │   │   ├── server.py         # MCP server implementation
  │   │   ├── resources.py      # MCP resources
  │   │   └── tools.py          # MCP tools
  │   ├── context_manager/
  │   │   ├── __init__.py
  │   │   ├── cli.py            # CLI interface
  │   │   ├── storage.py        # Database operations
  │   │   └── openai_client.py  # OpenAI API integration
  │   └── models.py             # Pydantic models
  ├── data/
  │   └── contexts.db           # SQLite database
  ├── config/
  │   └── mcp_config.json       # MCP server config for ChatGPT
  ├── requirements.txt
  ├── README.md
  └── PLAN.md
  ```

### Phase 2: Storage Layer

**2.1 Database Schema**
```sql
CREATE TABLE contexts (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,  -- JSON blob
    tags TEXT,              -- Comma-separated
    metadata TEXT,          -- JSON blob
    chatgpt_response TEXT
);

CREATE INDEX idx_type ON contexts(type);
CREATE INDEX idx_timestamp ON contexts(timestamp);
```

**2.2 Storage Module** (`storage.py`)
- `save_context()` - Insert new context entry
- `get_context(id)` - Retrieve by ID
- `list_contexts(filters)` - Query with filters
- `search_contexts(query)` - Full-text search
- `update_chatgpt_response(id, response)` - Store ChatGPT's reply

### Phase 3: Context Manager CLI

**3.1 Commands**

```bash
# Save context and get ChatGPT opinion (main workflow)
python -m context_manager save-and-query \
  --type suggestion \
  --title "Auth refactoring plan" \
  --content "..." \
  --tags "auth,refactoring"

# Just save without querying ChatGPT
python -m context_manager save \
  --type code \
  --title "New UserService implementation" \
  --file path/to/code.py

# Query ChatGPT about existing context
python -m context_manager query <context-id>

# List saved contexts
python -m context_manager list --type suggestion --limit 10

# Search contexts
python -m context_manager search "authentication"
```

**3.2 OpenAI Integration**

- Read `OPENAI_API_KEY` from environment
- Use `gpt-4` or `gpt-4-turbo` model
- System prompt: "You are a code review assistant. Provide a second opinion on the following context from Claude Code..."
- Return formatted response to console

### Phase 4: MCP Server

**4.1 Resources** (Read-only data for ChatGPT)

```python
# claude-context://recent
# Returns last 20 context entries

# claude-context://by-type/{type}
# Filter by conversation/code/suggestion/error

# claude-context://by-tag/{tag}
# Filter by tag

# claude-context://entry/{id}
# Specific context entry with full details
```

**4.2 Tools** (Actions ChatGPT can invoke)

```python
search_context(query: str, type: str = None, limit: int = 10)
# Full-text search across all contexts
# Returns: list of matching contexts

get_context_details(context_id: str)
# Retrieve complete context entry
# Returns: full context with code, messages, etc.

list_recent_contexts(limit: int = 20, type: str = None)
# Browse recent contexts
# Returns: list of context summaries

get_related_contexts(context_id: str, limit: int = 5)
# Find contexts with similar tags/content
# Returns: list of related contexts
```

**4.3 Server Configuration**

Create `config/mcp_config.json` for ChatGPT Desktop:
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

### Phase 5: Integration & Testing

**5.1 Claude Code Workflow**

User says: "Get a second opinion from ChatGPT on this authentication approach"

Claude Code executes:
```bash
python -m context_manager save-and-query \
  --type suggestion \
  --title "Authentication approach" \
  --content "$(cat <<'EOF'
[Context from conversation]
EOF
)"
```

Output displayed in Claude Code console:
```
✓ Context saved (ID: abc-123)
⏳ Querying ChatGPT...

ChatGPT's Second Opinion:
━━━━━━━━━━━━━━━━━━━━━━
[ChatGPT's detailed response]

✓ Response saved to context entry
```

**5.2 ChatGPT Desktop Workflow**

User opens ChatGPT Desktop and asks:
"What authentication suggestions did Claude Code make recently?"

ChatGPT uses MCP tools:
1. Calls `search_context(query="authentication", type="suggestion")`
2. Calls `get_context_details(context_id="abc-123")`
3. Provides analysis based on retrieved context

### Phase 6: Enhancements

**6.1 Rich Context Capture**
- Automatically capture file paths and line numbers
- Include git branch/commit info
- Attach related files automatically

**6.2 Conversation Threading**
- Link related contexts (original → refinement → final)
- Track evolution of ideas

**6.3 Web UI (Optional)**
- Simple Flask/FastAPI server to browse contexts
- Visualize conversation threads
- Manual editing/annotation

**6.4 Export/Import**
- Export contexts as markdown
- Import from Claude Code conversation logs
- Backup/restore database

## Tech Stack

### Core Dependencies

```txt
mcp>=0.1.0              # MCP SDK
pydantic>=2.0.0         # Data validation
openai>=1.0.0           # OpenAI API client
click>=8.0.0            # CLI framework
python-dotenv>=1.0.0    # Environment variables
aiosqlite>=0.19.0       # Async SQLite (for MCP server)
```

### Development Dependencies

```txt
pytest>=7.0.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
```

## Example Usage Scenarios

### Scenario 1: Code Review

```bash
# You're working on a new feature with Claude Code
# Claude suggests an implementation

# In Claude Code console:
User: "Get ChatGPT's opinion on this implementation"

# Claude Code runs:
python -m context_manager save-and-query \
  --type code \
  --title "UserService implementation" \
  --file src/user_service.py

# Output shows ChatGPT's review immediately
```

### Scenario 2: Architecture Decision

```bash
# Claude Code proposes database schema

User: "Let's get a second opinion on this schema design"

# Claude Code runs:
python -m context_manager save-and-query \
  --type suggestion \
  --title "Database schema for multi-tenancy" \
  --content "[schema discussion]"

# ChatGPT provides alternative approaches
```

### Scenario 3: Debugging

```bash
# Encountering a tricky bug

User: "Save this error log and ask ChatGPT for debugging ideas"

# Claude Code runs:
python -m context_manager save-and-query \
  --type error \
  --title "Auth middleware CORS issue" \
  --content "[error logs and context]"

# ChatGPT suggests debugging approaches
```

## Next Steps

1. Set up Python venv and install dependencies
2. Implement storage layer and models
3. Build Context Manager CLI
4. Implement MCP server with basic tools
5. Test full workflow end-to-end
6. Document usage and configuration

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=sk-...           # Required for OpenAI API
CHATMCP_DB_PATH=./data/contexts.db  # Optional, defaults to ./data/contexts.db
CHATMCP_MODEL=gpt-4             # Optional, defaults to gpt-4
```

### ChatGPT Desktop Setup

Add to ChatGPT Desktop settings:
1. Open Settings → Integrations → Model Context Protocol
2. Add server configuration from `config/mcp_config.json`
3. Restart ChatGPT Desktop
4. Verify connection with "List my recent Claude contexts"
