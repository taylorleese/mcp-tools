"""Storage layer for context entries using SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import ContextContent, ContextEntry


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
                    metadata TEXT,
                    chatgpt_response TEXT
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON contexts(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON contexts(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON contexts(title COLLATE NOCASE)")
            conn.commit()

    def save_context(self, context: ContextEntry) -> None:
        """Save a context entry to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO contexts
                (id, timestamp, type, title, content, tags, metadata, chatgpt_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    context.id,
                    context.timestamp.isoformat(),
                    context.type,
                    context.title,
                    context.content.model_dump_json(),
                    ",".join(context.tags),
                    json.dumps(context.metadata),
                    context.chatgpt_response,
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
        limit: int = 20,
        offset: int = 0,
    ) -> list[ContextEntry]:
        """List contexts with optional filters."""
        query = "SELECT * FROM contexts"
        params: list[Any] = []

        if type_filter:
            query += " WHERE type = ?"
            params.append(type_filter)

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

    def _row_to_context(self, row: sqlite3.Row) -> ContextEntry:
        """Convert a database row to a ContextEntry."""
        return ContextEntry(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            type=row["type"],
            title=row["title"],
            content=ContextContent.model_validate_json(row["content"]),
            tags=row["tags"].split(",") if row["tags"] else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            chatgpt_response=row["chatgpt_response"],
        )
