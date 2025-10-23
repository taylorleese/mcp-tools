"""MCP server for exposing Claude Code contexts to ChatGPT."""

import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from context_manager.storage import ContextStorage
from models import ContextEntry


class ContextMCPServer:
    """MCP server for Claude Code contexts."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("claude-context")
        # Use absolute path so it works regardless of cwd
        default_db = os.path.join(os.path.dirname(__file__), "..", "..", "data", "contexts.db")
        db_path = os.getenv("CHATMCP_DB_PATH", os.path.abspath(default_db))
        self.storage = ContextStorage(db_path)

        # Register handlers
        self.server.list_resources()(self.list_resources)
        self.server.read_resource()(self.read_resource)
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        return [
            Resource(
                uri=AnyUrl("claude-context://recent"),
                name="Recent Contexts",
                description="Last 20 context entries from Claude Code",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("claude-context://types/conversation"),
                name="Conversation Contexts",
                description="All conversation-type contexts",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("claude-context://types/code"),
                name="Code Contexts",
                description="All code-type contexts",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("claude-context://types/suggestion"),
                name="Suggestion Contexts",
                description="All suggestion-type contexts",
                mimeType="application/json",
            ),
            Resource(
                uri=AnyUrl("claude-context://types/error"),
                name="Error Contexts",
                description="All error/debugging contexts",
                mimeType="application/json",
            ),
        ]

    async def read_resource(self, uri: AnyUrl) -> str:
        """Read a resource by URI."""
        uri_str = str(uri)

        if uri_str == "claude-context://recent":
            contexts = self.storage.list_contexts(limit=20)
            return self._format_contexts_response(contexts)

        if uri_str.startswith("claude-context://types/"):
            context_type = uri_str.split("/")[-1]
            contexts = self.storage.list_contexts(type_filter=context_type, limit=50)
            return self._format_contexts_response(contexts)

        if uri_str.startswith("claude-context://entry/"):
            context_id = uri_str.split("/")[-1]
            context = self.storage.get_context(context_id)
            if not context:
                return f"Context {context_id} not found"
            return self._format_context_detail(context)

        return f"Unknown resource: {uri_str}"

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="search_context",
                description="Search Claude Code contexts by query string",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
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
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_context_details",
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
                name="list_recent_contexts",
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
                name="get_contexts_by_tags",
                description="Find contexts that match specific tags",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tags to search for",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10,
                        },
                    },
                    "required": ["tags"],
                },
            ),
        ]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool call."""
        if name == "search_context":
            query = arguments["query"]
            type_filter = arguments.get("type")
            limit = arguments.get("limit", 10)
            contexts = self.storage.search_contexts(query, type_filter=type_filter, limit=limit)
            result = self._format_contexts_response(contexts)
            return [TextContent(type="text", text=result)]

        if name == "get_context_details":
            context_id = arguments["context_id"]
            context = self.storage.get_context(context_id)
            if not context:
                return [TextContent(type="text", text=f"Context {context_id} not found")]
            result = self._format_context_detail(context)
            return [TextContent(type="text", text=result)]

        if name == "list_recent_contexts":
            limit = arguments.get("limit", 20)
            type_filter = arguments.get("type")
            contexts = self.storage.list_contexts(type_filter=type_filter, limit=limit)
            result = self._format_contexts_response(contexts)
            return [TextContent(type="text", text=result)]

        if name == "get_contexts_by_tags":
            tags = arguments["tags"]
            limit = arguments.get("limit", 10)
            contexts = self.storage.get_contexts_by_tags(tags, limit=limit)
            result = self._format_contexts_response(contexts)
            return [TextContent(type="text", text=result)]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    def _format_contexts_response(self, contexts: list[ContextEntry]) -> str:
        """Format a list of contexts for response."""
        if not contexts:
            return "No contexts found."

        lines = [f"Found {len(contexts)} contexts:\n"]
        for ctx in contexts:
            has_chatgpt = "✓" if ctx.chatgpt_response else "○"
            tags_str = f" [{', '.join(ctx.tags)}]" if ctx.tags else ""
            lines.append(f"{has_chatgpt} [{ctx.type}] {ctx.title}{tags_str}\n   ID: {ctx.id}\n   Timestamp: {ctx.timestamp.isoformat()}\n")
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

        return "\n".join(lines)

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())
