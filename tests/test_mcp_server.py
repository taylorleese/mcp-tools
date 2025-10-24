"""Tests for MCP server functionality."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_server.server import ContextMCPServer
from models import ContextEntry, TodoListSnapshot


@pytest.mark.integration
class TestMCPServerTools:
    """Test MCP server tool handlers."""

    @pytest.fixture
    def mcp_server(self, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> ContextMCPServer:
        """Create an MCP server instance with a temporary database."""
        monkeypatch.setenv("MCP_TOOLS_DB_PATH", temp_db_path)
        return ContextMCPServer()

    @pytest.mark.asyncio
    async def test_context_save_tool(self, mcp_server: ContextMCPServer) -> None:
        """Test the context_save tool."""
        # Mock the call_tool handler
        result = await mcp_server.call_tool(
            "context_save",
            {
                "type": "code",
                "title": "Test Save",
                "content": "Test content",
                "tags": ["test"],
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower() or "id" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_list_tool(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test the context_list tool."""
        # Save a context first
        mcp_server.storage.save_context(sample_context)

        # Call list tool
        result = await mcp_server.call_tool("context_list", {"limit": 10})

        assert result is not None
        assert len(result) > 0
        text = result[0].text
        assert "Test Context" in text or "contexts" in text.lower()

    @pytest.mark.asyncio
    async def test_context_search_tool(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test the context_search tool."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Search for it
        result = await mcp_server.call_tool("context_search", {"query": "test", "limit": 10})

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_context_get_tool(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test the context_get tool."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Get it by ID
        result = await mcp_server.call_tool("context_get", {"context_id": sample_context.id})

        assert result is not None
        text = result[0].text
        assert "Test Context" in text
        assert "test context" in text.lower()

    @pytest.mark.asyncio
    async def test_context_delete_tool(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test the context_delete tool."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Delete it
        result = await mcp_server.call_tool("context_delete", {"context_id": sample_context.id})

        assert result is not None
        assert "deleted" in result[0].text.lower()

        # Verify it's gone
        retrieved = mcp_server.storage.get_context(sample_context.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_todo_save_tool(self, mcp_server: ContextMCPServer) -> None:
        """Test the todo_save tool."""
        result = await mcp_server.call_tool(
            "todo_save",
            {
                "todos": [
                    {"content": "Task 1", "status": "pending", "activeForm": "Doing task 1"},
                    {"content": "Task 2", "status": "in_progress", "activeForm": "Doing task 2"},
                ],
                "context": "Test todos",
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower() or "snapshot" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_todo_list_tool(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test the todo_list tool."""
        # Save a snapshot first
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # List todos
        result = await mcp_server.call_tool("todo_list", {"limit": 10})

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_todo_restore_tool(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test the todo_restore tool."""
        # Save a snapshot
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # Restore it
        result = await mcp_server.call_tool("todo_restore", {"snapshot_id": sample_todo_snapshot.id})

        assert result is not None
        text = result[0].text
        assert "Task 1" in text or "todos" in text.lower()

    @pytest.mark.asyncio
    async def test_todo_get_tool(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test the todo_get tool."""
        # Save a snapshot
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # Get it
        result = await mcp_server.call_tool("todo_get", {"snapshot_id": sample_todo_snapshot.id})

        assert result is not None
        text = result[0].text
        assert "Task" in text

    @pytest.mark.asyncio
    async def test_todo_delete_tool(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test the todo_delete tool."""
        # Save a snapshot
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # Delete it
        result = await mcp_server.call_tool("todo_delete", {"snapshot_id": sample_todo_snapshot.id})

        assert result is not None
        assert "deleted" in result[0].text.lower()

        # Verify it's gone
        retrieved = mcp_server.storage.get_todo_snapshot(sample_todo_snapshot.id)
        assert retrieved is None

    @pytest.mark.asyncio
    @patch("mcp_server.server.ChatGPTClient")
    async def test_ask_chatgpt_tool(
        self,
        mock_chatgpt_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test the ask_chatgpt tool with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked ChatGPT response")
        mock_chatgpt_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask ChatGPT
        result = await mcp_server.call_tool("ask_chatgpt", {"context_id": sample_context.id})

        assert result is not None
        assert "Mocked ChatGPT response" in result[0].text

    @pytest.mark.asyncio
    @patch("mcp_server.server.ClaudeClient")
    async def test_ask_claude_tool(
        self,
        mock_claude_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test the ask_claude tool with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked Claude response")
        mock_claude_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask Claude
        result = await mcp_server.call_tool("ask_claude", {"context_id": sample_context.id})

        assert result is not None
        assert "Mocked Claude response" in result[0].text


@pytest.mark.integration
class TestMCPServerResources:
    """Test MCP server resource handlers."""

    @pytest.fixture
    def mcp_server(self, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> ContextMCPServer:
        """Create an MCP server instance with a temporary database."""
        monkeypatch.setenv("MCP_TOOLS_DB_PATH", temp_db_path)
        return ContextMCPServer()

    @pytest.mark.asyncio
    async def test_list_resources(self, mcp_server: ContextMCPServer) -> None:
        """Test listing available resources."""
        resources = await mcp_server.list_resources()

        assert len(resources) >= 4
        resource_uris = [str(r.uri) for r in resources]
        assert "mcp-toolz://contexts/project/recent" in resource_uris
        assert "mcp-toolz://todos/active" in resource_uris

    @pytest.mark.asyncio
    async def test_read_recent_contexts_resource(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test reading recent contexts resource."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Read the resource (need to mock os.getcwd)
        with patch("os.getcwd", return_value=sample_context.project_path):
            from pydantic import AnyUrl

            result = await mcp_server.read_resource(AnyUrl("mcp-toolz://contexts/project/recent"))

        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_read_active_todos_resource(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test reading active todos resource."""
        # Save a snapshot
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # Read the resource
        with patch("os.getcwd", return_value=sample_todo_snapshot.project_path):
            from pydantic import AnyUrl

            result = await mcp_server.read_resource(AnyUrl("mcp-toolz://todos/active"))

        assert result is not None
        assert isinstance(result, str)
