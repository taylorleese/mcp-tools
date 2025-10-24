"""MCP server for exposing Claude Code contexts to ChatGPT."""

import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from context_manager.anthropic_client import ClaudeClient
from context_manager.openai_client import ChatGPTClient
from context_manager.storage import ContextStorage
from models import ContextEntry


class ContextMCPServer:
    """MCP server for Claude Code contexts."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("mcp-toolz")
        # Use shared database location in home directory so all projects share the same data
        db_path = os.path.expanduser(os.getenv("MCP_TOOLS_DB_PATH", "~/.mcp-toolz/contexts.db"))
        self.storage = ContextStorage(db_path)

        # Generate session ID for this MCP server instance
        self.session_id = str(uuid4())
        self.session_timestamp = datetime.now(UTC)

        # Register handlers
        self.server.list_resources()(self.list_resources)  # type: ignore[no-untyped-call]
        self.server.read_resource()(self.read_resource)  # type: ignore[no-untyped-call]
        self.server.list_tools()(self.list_tools)  # type: ignore[no-untyped-call]
        self.server.call_tool()(self.call_tool)

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        return [
            # Project-based context resources
            Resource(
                uri=AnyUrl("mcp-toolz://contexts/project/recent"),
                name="Recent Project Contexts",
                description="Recent contexts for current project",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("mcp-toolz://contexts/project/sessions"),
                name="Project Sessions",
                description="List of recent Claude Code sessions for current project",
                mimeType="application/json",
            ),
            # Todo resources
            Resource(
                uri=AnyUrl("mcp-toolz://todos/recent"),
                name="Recent Todo Snapshots",
                description="Last 20 todo snapshots across all projects",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("mcp-toolz://todos/active"),
                name="Active Todo Snapshot",
                description="Active todo snapshot for current project",
                mimeType="application/json",
            ),
        ]

    async def read_resource(self, uri: AnyUrl) -> str:
        """Read a resource by URI."""
        uri_str = str(uri)
        project_path = os.getcwd()

        # Project-based context resources
        if uri_str == "mcp-toolz://contexts/project/recent":
            contexts = self.storage.list_contexts(project_path=project_path, limit=20)
            return self._format_contexts_response(contexts)

        if uri_str == "mcp-toolz://contexts/project/sessions":
            sessions = self.storage.list_sessions(project_path, limit=10)
            return self._format_sessions_response(sessions)

        if uri_str.startswith("mcp-toolz://contexts/session/"):
            session_id = uri_str.split("/")[-1]
            contexts = self.storage.get_session_contexts(session_id)
            return self._format_contexts_response(contexts)

        # Todo resources
        if uri_str == "mcp-toolz://todos/recent":
            snapshots = self.storage.list_todo_snapshots(limit=20)
            return self._format_todo_snapshots_response(snapshots)

        if uri_str == "mcp-toolz://todos/active":
            snapshot = self.storage.get_active_todo_snapshot(project_path)
            if not snapshot:
                return f"No active todo snapshot found for project: {project_path}"
            return self._format_todo_snapshot_detail(snapshot)

        return f"Unknown resource: {uri_str}"

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        return [
            # Context tools
            Tool(
                name="context_search",
                description="Search Claude Code contexts by query string or tags",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags",
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by type (conversation, code, suggestion, error)",
                            "enum": ["conversation", "code", "suggestion", "error"],
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                },
            ),
            Tool(
                name="context_get",
                description="Get full details of a specific context by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "context_id": {"type": "string", "description": "Context ID"},
                    },
                    "required": ["context_id"],
                },
            ),
            Tool(
                name="context_list",
                description="List recent Claude Code contexts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 20,
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by type (conversation, code, suggestion, error)",
                            "enum": ["conversation", "code", "suggestion", "error"],
                        },
                    },
                },
            ),
            Tool(
                name="context_delete",
                description="Delete a specific context by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "context_id": {"type": "string", "description": "Context ID to delete"},
                    },
                    "required": ["context_id"],
                },
            ),
            Tool(
                name="context_save",
                description="Save a new context entry for the current project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Context type",
                            "enum": ["conversation", "code", "suggestion", "error"],
                        },
                        "title": {"type": "string", "description": "Context title"},
                        "content": {"type": "string", "description": "Context content"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorization",
                        },
                        "session_context_id": {
                            "type": "string",
                            "description": "Link to existing context ID",
                        },
                    },
                    "required": ["type", "title", "content"],
                },
            ),
            # Todo tools
            Tool(
                name="todo_search",
                description="Search todo snapshots by content or context description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "project_path": {
                            "type": "string",
                            "description": "Filter by project path",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="todo_get",
                description="Get full details of a specific todo snapshot by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "snapshot_id": {"type": "string", "description": "Todo snapshot ID"},
                    },
                    "required": ["snapshot_id"],
                },
            ),
            Tool(
                name="todo_list",
                description="List recent todo snapshots",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 20,
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Filter by project path",
                        },
                    },
                },
            ),
            Tool(
                name="todo_save",
                description="Save a new todo snapshot",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "todos": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"},
                                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                                    "activeForm": {"type": "string"},
                                },
                                "required": ["content", "status", "activeForm"],
                            },
                            "description": "List of todo items",
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Project path (defaults to current directory)",
                        },
                        "context": {
                            "type": "string",
                            "description": "Description of what you're working on",
                        },
                        "session_context_id": {
                            "type": "string",
                            "description": "Link to existing context ID",
                        },
                    },
                    "required": ["todos"],
                },
            ),
            Tool(
                name="todo_restore",
                description="Get todo snapshot for restoring (active snapshot or specific ID)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "snapshot_id": {
                            "type": "string",
                            "description": "Specific snapshot ID (optional, defaults to active snapshot)",
                        },
                        "project_path": {
                            "type": "string",
                            "description": "Project path (used if snapshot_id not provided)",
                        },
                    },
                },
            ),
            Tool(
                name="todo_delete",
                description="Delete a specific todo snapshot by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "snapshot_id": {"type": "string", "description": "Todo snapshot ID to delete"},
                    },
                    "required": ["snapshot_id"],
                },
            ),
            # AI opinion tools
            Tool(
                name="ask_chatgpt",
                description="Ask ChatGPT a question about a context entry, or get a general second opinion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "context_id": {"type": "string", "description": "Context ID to ask about"},
                        "question": {
                            "type": "string",
                            "description": (
                                "Optional specific question to ask about the context. If not provided, gets a general second opinion."
                            ),
                        },
                    },
                    "required": ["context_id"],
                },
            ),
            Tool(
                name="ask_claude",
                description="Ask Claude a question about a context entry, or get a general second opinion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "context_id": {"type": "string", "description": "Context ID to ask about"},
                        "question": {
                            "type": "string",
                            "description": (
                                "Optional specific question to ask about the context. If not provided, gets a general second opinion."
                            ),
                        },
                    },
                    "required": ["context_id"],
                },
            ),
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool call."""
        # Context tools
        if name == "context_search":
            query = arguments.get("query")
            tags = arguments.get("tags")
            type_filter = arguments.get("type")
            limit = arguments.get("limit", 10)

            # If tags provided, search by tags; otherwise search by query
            if tags:
                contexts = self.storage.get_contexts_by_tags(tags, limit=limit)
            elif query:
                contexts = self.storage.search_contexts(query, type_filter=type_filter, limit=limit)
            else:
                contexts = self.storage.list_contexts(type_filter=type_filter, limit=limit)

            result = self._format_contexts_response(contexts)
            return [TextContent(type="text", text=result)]

        if name == "context_get":
            context_id = arguments["context_id"]
            context = self.storage.get_context(context_id)
            if not context:
                return [TextContent(type="text", text=f"Context {context_id} not found")]
            result = self._format_context_detail(context)
            return [TextContent(type="text", text=result)]

        if name == "context_list":
            limit = arguments.get("limit", 20)
            type_filter = arguments.get("type")
            contexts = self.storage.list_contexts(type_filter=type_filter, limit=limit)
            result = self._format_contexts_response(contexts)
            return [TextContent(type="text", text=result)]

        if name == "context_delete":
            context_id = arguments["context_id"]
            deleted = self.storage.delete_context(context_id)
            if deleted:
                return [TextContent(type="text", text=f"✓ Context {context_id} deleted")]
            return [TextContent(type="text", text=f"Context {context_id} not found")]

        if name == "context_save":
            from models import ContextContent

            context_type = arguments["type"]
            title = arguments["title"]
            content_text = arguments["content"]
            tags = arguments.get("tags", [])
            session_context_id = arguments.get("session_context_id")

            # Parse content based on type
            if context_type == "conversation":
                content = ContextContent(messages=[content_text])
            elif context_type == "code":
                content = ContextContent(code={"snippet": content_text})
            elif context_type == "suggestion":
                content = ContextContent(suggestions=content_text)
            elif context_type == "error":
                content = ContextContent(errors=content_text)
            else:
                content = ContextContent(messages=[content_text])

            # Create context entry with session info
            context = ContextEntry(
                type=context_type,
                title=title,
                content=content,
                tags=tags,
                project_path=os.getcwd(),
                session_id=self.session_id,
                session_timestamp=self.session_timestamp,
            )

            # Link to session context if provided
            if session_context_id:
                context.metadata["session_context_id"] = session_context_id

            self.storage.save_context(context)
            return [TextContent(type="text", text=f"✓ Context saved (ID: {context.id})")]

        # Todo tools
        if name == "todo_search":
            query = arguments["query"]
            project_path = arguments.get("project_path")
            limit = arguments.get("limit", 10)
            snapshots = self.storage.search_todo_snapshots(query, project_path=project_path, limit=limit)
            result = self._format_todo_snapshots_response(snapshots)
            return [TextContent(type="text", text=result)]

        if name == "todo_get":
            snapshot_id = arguments["snapshot_id"]
            snapshot = self.storage.get_todo_snapshot(snapshot_id)
            if not snapshot:
                return [TextContent(type="text", text=f"Todo snapshot {snapshot_id} not found")]
            result = self._format_todo_snapshot_detail(snapshot)
            return [TextContent(type="text", text=result)]

        if name == "todo_list":
            limit = arguments.get("limit", 20)
            project_path = arguments.get("project_path")
            snapshots = self.storage.list_todo_snapshots(project_path=project_path, limit=limit)
            result = self._format_todo_snapshots_response(snapshots)
            return [TextContent(type="text", text=result)]

        if name == "todo_save":
            from models import Todo, TodoListSnapshot

            todos_data = arguments["todos"]
            todos = [Todo(**todo) for todo in todos_data]
            project_path = arguments.get("project_path", os.getcwd())
            context = arguments.get("context")
            session_context_id = arguments.get("session_context_id")

            snapshot = TodoListSnapshot(
                project_path=project_path,
                todos=todos,
                context=context,
                session_context_id=session_context_id,
                is_active=True,
            )

            self.storage.save_todo_snapshot(snapshot)
            return [TextContent(type="text", text=f"✓ Todo snapshot saved (ID: {snapshot.id})")]

        if name == "todo_restore":
            snapshot_id = arguments.get("snapshot_id")
            project_path = arguments.get("project_path", os.getcwd())

            snapshot = self.storage.get_todo_snapshot(snapshot_id) if snapshot_id else self.storage.get_active_todo_snapshot(project_path)

            if not snapshot:
                return [TextContent(type="text", text="No todo snapshot found")]

            result = self._format_todo_snapshot_detail(snapshot)
            return [TextContent(type="text", text=result)]

        if name == "todo_delete":
            snapshot_id = arguments["snapshot_id"]
            deleted = self.storage.delete_todo_snapshot(snapshot_id)
            if deleted:
                return [TextContent(type="text", text=f"✓ Todo snapshot {snapshot_id} deleted")]
            return [TextContent(type="text", text=f"Todo snapshot {snapshot_id} not found")]

        # AI opinion tools
        if name == "ask_chatgpt":
            context_id = arguments["context_id"]
            question = arguments.get("question")
            context = self.storage.get_context(context_id)
            if not context:
                return [TextContent(type="text", text=f"Context {context_id} not found")]

            try:
                chatgpt_client = ChatGPTClient()
                response = chatgpt_client.get_second_opinion(context, question)

                # Only save to database if it's a generic second opinion (no custom question)
                if not question:
                    self.storage.update_chatgpt_response(context_id, response)

                header = "ChatGPT's Answer:" if question else "ChatGPT's Opinion:"
                return [TextContent(type="text", text=f"{header}\n\n{response}")]
            except ValueError as e:
                return [TextContent(type="text", text=f"Error: {e}")]

        if name == "ask_claude":
            context_id = arguments["context_id"]
            question = arguments.get("question")
            context = self.storage.get_context(context_id)
            if not context:
                return [TextContent(type="text", text=f"Context {context_id} not found")]

            try:
                claude_client = ClaudeClient()
                response = claude_client.get_second_opinion(context, question)

                # Only save to database if it's a generic second opinion (no custom question)
                if not question:
                    self.storage.update_claude_response(context_id, response)

                header = "Claude's Answer:" if question else "Claude's Opinion:"
                return [TextContent(type="text", text=f"{header}\n\n{response}")]
            except ValueError as e:
                return [TextContent(type="text", text=f"Error: {e}")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    def _format_contexts_response(self, contexts: list[ContextEntry]) -> str:
        """Format a list of contexts for response."""
        if not contexts:
            return "No contexts found."

        lines = [f"Found {len(contexts)} contexts:\n"]
        for ctx in contexts:
            chatgpt_icon = "✓" if ctx.chatgpt_response else "○"
            claude_icon = "✓" if ctx.claude_response else "○"
            tags_str = f" [{', '.join(ctx.tags)}]" if ctx.tags else ""
            lines.append(
                f"GPT:{chatgpt_icon} Claude:{claude_icon} [{ctx.type}] {ctx.title}{tags_str}\n"
                f"   ID: {ctx.id}\n   Timestamp: {ctx.timestamp.isoformat()}\n"
            )
        return "\n".join(lines)

    def _format_context_detail(self, context: Any) -> str:
        """Format a single context with full details."""
        lines = [
            f"Title: {context.title}",
            f"Type: {context.type}",
            f"ID: {context.id}",
            f"Timestamp: {context.timestamp.isoformat()}",
        ]

        if context.tags:
            lines.append(f"Tags: {', '.join(context.tags)}")

        lines.append("\n## Content\n")

        if context.content.messages:
            lines.append("### Conversation:")
            for msg in context.content.messages:
                lines.append(msg)

        if context.content.code:
            lines.append("\n### Code:")
            for file_path, code in context.content.code.items():
                lines.append(f"\nFile: {file_path}")
                lines.append(f"```\n{code}\n```")

        if context.content.suggestions:
            lines.append(f"\n### Suggestion:\n{context.content.suggestions}")

        if context.content.errors:
            lines.append(f"\n### Errors:\n{context.content.errors}")

        if context.chatgpt_response:
            lines.append(f"\n## ChatGPT's Previous Response:\n{context.chatgpt_response}")

        if context.claude_response:
            lines.append(f"\n## Claude's Previous Response:\n{context.claude_response}")

        return "\n".join(lines)

    def _format_sessions_response(self, sessions: list[dict[str, Any]]) -> str:
        """Format a list of sessions for response."""
        if not sessions:
            return "No sessions found for this project."

        lines = ["Recent Claude Code sessions for this project:\n"]
        for session in sessions:
            session_time = datetime.fromisoformat(session["session_timestamp"])
            context_count = session["context_count"]
            lines.append(
                f"Session: {session_time.strftime('%Y-%m-%d %I:%M %p')} ({context_count} contexts)\n"
                f"   Session ID: {session['session_id']}\n"
                f"   Resource: mcp-toolz://contexts/session/{session['session_id']}\n"
            )
        return "\n".join(lines)

    def _format_todo_snapshots_response(self, snapshots: list[Any]) -> str:
        """Format a list of todo snapshots for response."""
        from models import TodoListSnapshot

        if not snapshots:
            return "No todo snapshots found."

        lines = [f"Found {len(snapshots)} todo snapshots:\n"]
        for snapshot in snapshots:
            if isinstance(snapshot, TodoListSnapshot):
                active_icon = "★" if snapshot.is_active else "○"
                completed = sum(1 for t in snapshot.todos if t.status == "completed")
                total = len(snapshot.todos)
                context_str = f" - {snapshot.context}" if snapshot.context else ""

                lines.append(
                    f"{active_icon} {snapshot.timestamp.isoformat()}\n"
                    f"   ID: {snapshot.id}\n"
                    f"   Project: {snapshot.project_path}\n"
                    f"   Progress: {completed}/{total} completed{context_str}\n"
                )
        return "\n".join(lines)

    def _format_todo_snapshot_detail(self, snapshot: Any) -> str:
        """Format a single todo snapshot with full details."""
        from models import TodoListSnapshot

        if not isinstance(snapshot, TodoListSnapshot):
            return "Invalid snapshot"

        lines = [
            f"Snapshot ID: {snapshot.id}",
            f"Timestamp: {snapshot.timestamp.isoformat()}",
            f"Project: {snapshot.project_path}",
            f"Active: {'Yes' if snapshot.is_active else 'No'}",
        ]

        if snapshot.context:
            lines.append(f"Context: {snapshot.context}")

        if snapshot.session_context_id:
            lines.append(f"Linked Context ID: {snapshot.session_context_id}")

        lines.append("\n## Todo Items\n")

        for i, todo in enumerate(snapshot.todos, 1):
            status_icon = {"pending": "○", "in_progress": "⟳", "completed": "✓"}.get(todo.status, "○")
            lines.append(f"{i}. {status_icon} [{todo.status}] {todo.content}")

        return "\n".join(lines)

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
