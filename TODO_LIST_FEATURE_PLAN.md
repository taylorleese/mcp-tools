# Todo List Persistence Feature Plan

## Overview

Add todo list persistence to allow saving and restoring todo lists across Claude Code sessions, preventing loss of todos when restarting.

## Core Features

### 1. Save/Restore Todo Lists
- Snapshot current todos with timestamp
- Associate with project/session
- Restore on demand or auto-restore

### 2. Context Association
- Save what you were working on
- Link to project path, git branch
- Optional description

### 3. Multiple Snapshots
- Keep history of todo lists
- Switch between different task sets
- Track progress over time

## Data Model

```python
TodoListSnapshot {
  id: UUID
  timestamp: datetime
  project_path: str  # /Users/tleese/claude-context
  git_branch: str | null  # main, feature/xyz
  todos: list[Todo]  # The actual todo items
  context: str | null  # Optional: what you were working on
  session_context_id: str | null  # Link to a saved context entry
  is_active: bool  # Current active list for this project
}

Todo {
  content: str
  status: "pending" | "in_progress" | "completed"
  activeForm: str
}
```

## CLI Commands

### Save Todos
```bash
# Save current todos (manual paste)
./claude-context save-todos \
  --context "Working on MCP server bug fixes" \
  --tags "mcp,bugfix"

# Link todos to existing context
./claude-context save-todos --link-context <context-id>
```

### Restore Todos
```bash
# Restore last todos for current project
./claude-context restore-todos

# Restore specific snapshot
./claude-context restore-todos <snapshot-id>
```

### List & View
```bash
# List all saved todo snapshots
./claude-context list-todo-snapshots

# Show specific snapshot
./claude-context show-todo-snapshot <id>

# Show history for current project
./claude-context todo-history
```

## MCP Tools Integration

New MCP tools for Claude Code to use:

### `save_current_todos`
**Input:**
- `todos`: list of todo items (from TodoWrite tool)
- `context`: optional description
- `link_context_id`: optional link to existing context

**Output:**
- Snapshot ID
- Confirmation message

### `restore_todos`
**Input:**
- `snapshot_id`: optional (defaults to latest for current project)

**Output:**
- List of todos to restore
- Context information

### `list_todo_snapshots`
**Input:**
- `project_path`: optional filter
- `limit`: number of results

**Output:**
- List of snapshots with metadata

### `search_todo_history`
**Input:**
- `query`: search term
- `project_path`: optional filter

**Output:**
- Matching snapshots

## Auto-Integration Options

### Option 1: Manual workflow (simple)
- User copies/paste todos when saving
- Claude helps restore by showing saved lists

### Option 2: MCP tool workflow (better) ⭐ RECOMMENDED
- Claude can call `save_todos` tool with current todos
- Auto-detect project and save
- Auto-restore when user asks
- Seamless integration

### Option 3: File watching (advanced)
- Watch `.claude.json` or session files
- Auto-save on changes
- Auto-restore on project open

## Implementation Plan

### Phase 1: Database Schema
1. Create `todo_snapshots` table
2. Add models for TodoListSnapshot and Todo
3. Update storage layer

### Phase 2: CLI Commands
1. Implement `save-todos` command
2. Implement `restore-todos` command
3. Implement `list-todo-snapshots` command
4. Implement `show-todo-snapshot` command

### Phase 3: MCP Integration
1. Add MCP tools for saving/restoring
2. Update MCP server with new tools
3. Test from Claude Code sessions

### Phase 4: Enhancements
1. Auto-detection of project path
2. Git branch tracking
3. Context linking
4. Progress analytics

## Database Schema

```sql
CREATE TABLE todo_snapshots (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    project_path TEXT NOT NULL,
    git_branch TEXT,
    context TEXT,
    session_context_id TEXT,
    is_active INTEGER DEFAULT 0,
    todos TEXT NOT NULL,  -- JSON array of todo items
    metadata TEXT,  -- JSON blob for future expansion
    FOREIGN KEY (session_context_id) REFERENCES contexts(id)
);

CREATE INDEX idx_todo_project ON todo_snapshots(project_path);
CREATE INDEX idx_todo_timestamp ON todo_snapshots(timestamp);
CREATE INDEX idx_todo_active ON todo_snapshots(is_active);
CREATE INDEX idx_todo_branch ON todo_snapshots(git_branch);
```

## Usage Examples

### Example 1: Save todos at end of session

```bash
./claude-context save-todos \
  --context "Finished implementing MCP server, need to add error handling next" \
  --tags "mcp,in-progress"
```

### Example 2: Restore todos next day

User in Claude Code: "What was I working on yesterday?"

Claude uses MCP tool → retrieves last snapshot → shows todos and context

### Example 3: Link todos to design decision

```bash
# First save a context
./claude-context save --type suggestion --title "Architecture decision" --content "..."

# Then save todos linked to it
./claude-context save-todos --link-context <context-id>
```

## Design Questions & Decisions

### Q1: How to capture current todos?
**Decision:** Option 2 - MCP tool workflow
- Claude intercepts TodoWrite calls or user explicitly asks to save
- Most seamless UX

### Q2: When to auto-restore?
**Decision:** On demand only
- User asks: "Restore my todos" or "What was I working on?"
- Prevents unwanted overwrites

### Q3: Context linking
**Decision:** Optional both ways
- Todos can optionally create/link to context
- Contexts can optionally save current todos
- Flexible for different workflows

### Q4: Scope
**Decision:** Per-project with global search
- Each project has its own active snapshot
- Can search/view across all projects
- Balances isolation and discoverability

## Success Metrics

- ✅ Never lose todos when restarting Claude Code
- ✅ Quick restore (<5 seconds)
- ✅ Intuitive commands
- ✅ Seamless MCP integration
- ✅ Historical tracking for progress review

## Future Enhancements

1. **Todo Analytics**
   - Completion rates
   - Time tracking per todo
   - Velocity metrics

2. **Team Sharing**
   - Export todo snapshots
   - Import from team members
   - Shared project todos

3. **Smart Suggestions**
   - Claude suggests todos based on context
   - Auto-prioritization
   - Dependency tracking

4. **Integration**
   - Export to TODO.md files
   - Sync with external tools (Jira, Linear, etc.)
   - Calendar integration

## Notes

- Keep it simple initially - focus on save/restore
- Can expand later based on usage patterns
- Prioritize reliability over features
