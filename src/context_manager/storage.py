"""Storage layer for context entries using SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from models import ContextContent, ContextEntry, Todo, TodoListSnapshot


class ContextStorage:
    """Manages storage and retrieval of context entries."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize storage with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS contexts (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    project_path TEXT NOT NULL,
                    session_id TEXT,
                    session_timestamp TEXT,
                    metadata TEXT,
                    chatgpt_response TEXT,
                    claude_response TEXT
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON contexts(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON contexts(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON contexts(title COLLATE NOCASE)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_project_path ON contexts(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON contexts(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_timestamp ON contexts(session_timestamp)")

            # Todo snapshots table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS todo_snapshots (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    git_branch TEXT,
                    context TEXT,
                    session_context_id TEXT,
                    is_active INTEGER DEFAULT 0,
                    todos TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (session_context_id) REFERENCES contexts(id)
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todo_project ON todo_snapshots(project_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todo_timestamp ON todo_snapshots(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todo_active ON todo_snapshots(is_active)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_todo_branch ON todo_snapshots(git_branch)")

            conn.commit()

    def save_context(self, context: ContextEntry) -> None:
        """Save a context entry to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO contexts
                (id, timestamp, type, title, content, tags, project_path, session_id,
                 session_timestamp, metadata, chatgpt_response, claude_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    context.id,
                    context.timestamp.isoformat(),
                    context.type,
                    context.title,
                    context.content.model_dump_json(),
                    ",".join(context.tags),
                    context.project_path,
                    context.session_id,
                    context.session_timestamp.isoformat() if context.session_timestamp else None,
                    json.dumps(context.metadata),
                    context.chatgpt_response,
                    context.claude_response,
                ),
            )
            conn.commit()

    def get_context(self, context_id: str) -> ContextEntry | None:
        """Retrieve a context entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM contexts WHERE id = ?", (context_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_context(row)

    def list_contexts(
        self,
        type_filter: str | None = None,
        project_path: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ContextEntry]:
        """List contexts with optional filters."""
        query = "SELECT * FROM contexts"
        params: list[Any] = []
        conditions = []

        if type_filter:
            conditions.append("type = ?")
            params.append(type_filter)

        if project_path:
            conditions.append("project_path = ?")
            params.append(project_path)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_context(row) for row in cursor.fetchall()]

    def search_contexts(self, query: str, type_filter: str | None = None, limit: int = 10) -> list[ContextEntry]:
        """Search contexts by title, content, or tags."""
        sql_query = """
            SELECT * FROM contexts
            WHERE (
                title LIKE ? OR
                content LIKE ? OR
                tags LIKE ?
            )
        """
        params: list[Any] = [f"%{query}%", f"%{query}%", f"%{query}%"]

        if type_filter:
            sql_query += " AND type = ?"
            params.append(type_filter)

        sql_query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql_query, params)
            return [self._row_to_context(row) for row in cursor.fetchall()]

    def update_chatgpt_response(self, context_id: str, response: str) -> None:
        """Update the ChatGPT response for a context."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE contexts SET chatgpt_response = ? WHERE id = ?",
                (response, context_id),
            )
            conn.commit()

    def update_claude_response(self, context_id: str, response: str) -> None:
        """Update the Claude response for a context."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE contexts SET claude_response = ? WHERE id = ?",
                (response, context_id),
            )
            conn.commit()

    def delete_context(self, context_id: str) -> bool:
        """Delete a context by ID. Returns True if deleted, False if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM contexts WHERE id = ?", (context_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_contexts_by_tags(self, tags: list[str], limit: int = 10) -> list[ContextEntry]:
        """Get contexts that match any of the given tags."""
        # Build OR conditions for each tag (using parameterized queries)
        conditions = " OR ".join(["tags LIKE ?"] * len(tags))
        # Safe: only concatenating placeholders, user data goes through params
        query = "SELECT * FROM contexts WHERE " + conditions + " ORDER BY timestamp DESC LIMIT ?"  # nosec B608
        params = [f"%{tag}%" for tag in tags] + [limit]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_context(row) for row in cursor.fetchall()]

    def list_sessions(self, project_path: str, limit: int = 10) -> list[dict[str, Any]]:
        """List recent sessions for a project (grouped by session_id)."""
        query = """
            SELECT
                session_id,
                session_timestamp,
                COUNT(*) as context_count,
                MIN(timestamp) as first_context,
                MAX(timestamp) as last_context
            FROM contexts
            WHERE project_path = ? AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY session_timestamp DESC
            LIMIT ?
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (project_path, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_session_contexts(self, session_id: str) -> list[ContextEntry]:
        """Get all contexts from a specific session."""
        query = "SELECT * FROM contexts WHERE session_id = ? ORDER BY timestamp ASC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (session_id,))
            return [self._row_to_context(row) for row in cursor.fetchall()]

    def _row_to_context(self, row: sqlite3.Row) -> ContextEntry:
        """Convert a database row to a ContextEntry."""
        return ContextEntry(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            type=row["type"],
            title=row["title"],
            content=ContextContent.model_validate_json(row["content"]),
            tags=row["tags"].split(",") if row["tags"] else [],
            project_path=row["project_path"],
            session_id=row["session_id"],
            session_timestamp=datetime.fromisoformat(row["session_timestamp"]) if row["session_timestamp"] else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            chatgpt_response=row["chatgpt_response"],
            claude_response=row["claude_response"],
        )

    # Todo snapshot methods

    def save_todo_snapshot(self, snapshot: TodoListSnapshot) -> None:
        """Save a todo list snapshot to the database."""
        with sqlite3.connect(self.db_path) as conn:
            # Mark other snapshots for this project as inactive
            if snapshot.is_active:
                conn.execute(
                    "UPDATE todo_snapshots SET is_active = 0 WHERE project_path = ?",
                    (snapshot.project_path,),
                )

            conn.execute(
                """
                INSERT OR REPLACE INTO todo_snapshots
                (id, timestamp, project_path, git_branch, context, session_context_id,
                 is_active, todos, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.id,
                    snapshot.timestamp.isoformat(),
                    snapshot.project_path,
                    snapshot.git_branch,
                    snapshot.context,
                    snapshot.session_context_id,
                    1 if snapshot.is_active else 0,
                    json.dumps([todo.model_dump() for todo in snapshot.todos]),
                    json.dumps(snapshot.metadata),
                ),
            )
            conn.commit()

    def get_todo_snapshot(self, snapshot_id: str) -> TodoListSnapshot | None:
        """Retrieve a todo snapshot by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM todo_snapshots WHERE id = ?", (snapshot_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_todo_snapshot(row)

    def get_active_todo_snapshot(self, project_path: str) -> TodoListSnapshot | None:
        """Get the active todo snapshot for a project."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM todo_snapshots WHERE project_path = ? AND is_active = 1",
                (project_path,),
            )
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_todo_snapshot(row)

    def list_todo_snapshots(
        self,
        project_path: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[TodoListSnapshot]:
        """List todo snapshots with optional filters."""
        query = "SELECT * FROM todo_snapshots"
        params: list[Any] = []

        if project_path:
            query += " WHERE project_path = ?"
            params.append(project_path)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_todo_snapshot(row) for row in cursor.fetchall()]

    def search_todo_snapshots(
        self,
        query: str,
        project_path: str | None = None,
        limit: int = 10,
    ) -> list[TodoListSnapshot]:
        """Search todo snapshots by content or context description."""
        sql_query = """
            SELECT * FROM todo_snapshots
            WHERE (
                todos LIKE ? OR
                context LIKE ?
            )
        """
        params: list[Any] = [f"%{query}%", f"%{query}%"]

        if project_path:
            sql_query += " AND project_path = ?"
            params.append(project_path)

        sql_query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql_query, params)
            return [self._row_to_todo_snapshot(row) for row in cursor.fetchall()]

    def delete_todo_snapshot(self, snapshot_id: str) -> bool:
        """Delete a todo snapshot by ID. Returns True if deleted, False if not found."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM todo_snapshots WHERE id = ?", (snapshot_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_todo_snapshot(self, row: sqlite3.Row) -> TodoListSnapshot:
        """Convert a database row to a TodoListSnapshot."""
        todos_data = json.loads(row["todos"])
        todos = [Todo(**todo) for todo in todos_data]

        return TodoListSnapshot(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            project_path=row["project_path"],
            git_branch=row["git_branch"],
            context=row["context"],
            session_context_id=row["session_context_id"],
            is_active=bool(row["is_active"]),
            todos=todos,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
