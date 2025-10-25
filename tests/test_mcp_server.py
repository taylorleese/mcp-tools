"""Tests for MCP server functionality."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.server import ContextMCPServer
from models import ContextEntry, TodoListSnapshot


@pytest.mark.integration
class TestMCPServerTools:
    """Test MCP server tool handlers."""

    @pytest.fixture
    def mcp_server(self, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> Generator[ContextMCPServer]:
        """Create an MCP server instance with a temporary database."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
        server = ContextMCPServer()
        yield server
        server.storage.close()

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

    @patch("mcp_server.server.GeminiClient")
    async def test_ask_gemini_tool(
        self,
        mock_gemini_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test the ask_gemini tool with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked Gemini response")
        mock_gemini_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask Gemini
        result = await mcp_server.call_tool("ask_gemini", {"context_id": sample_context.id})

        assert result is not None
        assert "Mocked Gemini response" in result[0].text

    @patch("mcp_server.server.DeepSeekClient")
    async def test_ask_deepseek_tool(
        self,
        mock_deepseek_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test the ask_deepseek tool with mocked API."""
        # Setup mock
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked DeepSeek response")
        mock_deepseek_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask DeepSeek
        result = await mcp_server.call_tool("ask_deepseek", {"context_id": sample_context.id})

        assert result is not None
        assert "Mocked DeepSeek response" in result[0].text


@pytest.mark.integration
class TestMCPServerResources:
    """Test MCP server resource handlers."""

    @pytest.fixture
    def mcp_server(self, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> Generator[ContextMCPServer]:
        """Create an MCP server instance with a temporary database."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
        server = ContextMCPServer()
        yield server
        server.storage.close()

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

    @pytest.mark.asyncio
    async def test_context_get_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test getting a non-existent context."""
        result = await mcp_server.call_tool("context_get", {"context_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_delete_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test deleting a non-existent context."""
        result = await mcp_server.call_tool("context_delete", {"context_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_save_with_suggestion(self, mcp_server: ContextMCPServer) -> None:
        """Test saving a suggestion-type context."""
        result = await mcp_server.call_tool(
            "context_save",
            {
                "type": "suggestion",
                "title": "Test Suggestion",
                "content": "Use type hints",
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_save_with_error(self, mcp_server: ContextMCPServer) -> None:
        """Test saving an error-type context."""
        result = await mcp_server.call_tool(
            "context_save",
            {
                "type": "error",
                "title": "Test Error",
                "content": "TypeError: expected str",
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_save_with_conversation(self, mcp_server: ContextMCPServer) -> None:
        """Test saving a conversation-type context."""
        result = await mcp_server.call_tool(
            "context_save",
            {
                "type": "conversation",
                "title": "Test Conversation",
                "content": "Hello, how are you?",
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_save_with_session_context_id(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test saving context with session_context_id."""
        # First save a parent context
        mcp_server.storage.save_context(sample_context)

        result = await mcp_server.call_tool(
            "context_save",
            {
                "type": "code",
                "title": "Child Context",
                "content": "Related code",
                "session_context_id": sample_context.id,
            },
        )

        assert result is not None
        assert "saved" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_context_search_by_tags(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test searching contexts by tags."""
        # Save a context with tags
        sample_context.tags = ["python", "test"]
        mcp_server.storage.save_context(sample_context)

        result = await mcp_server.call_tool("context_search", {"tags": ["python"], "limit": 10})

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_context_search_without_query(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test context_search without query or tags (should list all)."""
        mcp_server.storage.save_context(sample_context)

        result = await mcp_server.call_tool("context_search", {"limit": 10})

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_todo_get_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test getting a non-existent todo snapshot."""
        result = await mcp_server.call_tool("todo_get", {"snapshot_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_todo_delete_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test deleting a non-existent todo snapshot."""
        result = await mcp_server.call_tool("todo_delete", {"snapshot_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_todo_restore_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test restoring non-existent todo snapshot."""
        result = await mcp_server.call_tool("todo_restore", {})

        assert result is not None
        assert "not found" in result[0].text.lower() or "no todo" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_ask_chatgpt_context_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test ask_chatgpt with non-existent context."""
        result = await mcp_server.call_tool("ask_chatgpt", {"context_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_ask_claude_context_not_found(self, mcp_server: ContextMCPServer) -> None:
        """Test ask_claude with non-existent context."""
        result = await mcp_server.call_tool("ask_claude", {"context_id": "nonexistent"})

        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_read_unknown_resource(self, mcp_server: ContextMCPServer) -> None:
        """Test reading an unknown resource."""
        from pydantic import AnyUrl

        result = await mcp_server.read_resource(AnyUrl("mcp-toolz://unknown/path"))

        assert result is not None
        assert "unknown" in result.lower()

    @pytest.mark.asyncio
    async def test_read_recent_todos_resource(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test reading recent todos resource."""
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        from pydantic import AnyUrl

        result = await mcp_server.read_resource(AnyUrl("mcp-toolz://todos/recent"))

        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_read_active_todos_no_snapshot(self, mcp_server: ContextMCPServer) -> None:
        """Test reading active todos when no snapshot exists."""
        with patch("os.getcwd", return_value="/nonexistent"):
            from pydantic import AnyUrl

            result = await mcp_server.read_resource(AnyUrl("mcp-toolz://todos/active"))

        assert result is not None
        assert "no active" in result.lower() or "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_server: ContextMCPServer) -> None:
        """Test listing available tools."""
        tools = await mcp_server.list_tools()

        assert len(tools) >= 14
        tool_names = [t.name for t in tools]
        assert "context_search" in tool_names
        assert "context_get" in tool_names
        assert "context_list" in tool_names
        assert "context_delete" in tool_names
        assert "context_save" in tool_names
        assert "todo_search" in tool_names
        assert "todo_get" in tool_names
        assert "todo_list" in tool_names
        assert "todo_save" in tool_names
        assert "todo_restore" in tool_names
        assert "todo_delete" in tool_names
        assert "ask_chatgpt" in tool_names
        assert "ask_claude" in tool_names
        assert "ask_gemini" in tool_names
        assert "ask_deepseek" in tool_names

    @pytest.mark.asyncio
    async def test_todo_search_tool(self, mcp_server: ContextMCPServer, sample_todo_snapshot: TodoListSnapshot) -> None:
        """Test the todo_search tool."""
        # Save a snapshot
        mcp_server.storage.save_todo_snapshot(sample_todo_snapshot)

        # Search for it
        result = await mcp_server.call_tool("todo_search", {"query": "Task", "limit": 10})

        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_unknown_tool(self, mcp_server: ContextMCPServer) -> None:
        """Test calling an unknown tool."""
        result = await mcp_server.call_tool("unknown_tool_name", {})

        assert result is not None
        assert "unknown" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("mcp_server.server.ChatGPTClient")
    async def test_ask_chatgpt_error_handling(
        self,
        mock_chatgpt_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test ask_chatgpt error handling."""
        # Setup mock to raise ValueError
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(side_effect=ValueError("API key missing"))
        mock_chatgpt_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask ChatGPT (should handle error)
        result = await mcp_server.call_tool("ask_chatgpt", {"context_id": sample_context.id})

        assert result is not None
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("mcp_server.server.ClaudeClient")
    async def test_ask_claude_error_handling(
        self,
        mock_claude_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test ask_claude error handling."""
        # Setup mock to raise ValueError
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(side_effect=ValueError("API key missing"))
        mock_claude_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask Claude (should handle error)
        result = await mcp_server.call_tool("ask_claude", {"context_id": sample_context.id})

        assert result is not None
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("mcp_server.server.GeminiClient")
    async def test_ask_gemini_error_handling(
        self,
        mock_gemini_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test ask_gemini error handling."""
        # Setup mock to raise ValueError
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(side_effect=ValueError("API key missing"))
        mock_gemini_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask Gemini (should handle error)
        result = await mcp_server.call_tool("ask_gemini", {"context_id": sample_context.id})

        assert result is not None
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch("mcp_server.server.DeepSeekClient")
    async def test_ask_deepseek_error_handling(
        self,
        mock_deepseek_class: MagicMock,
        mcp_server: ContextMCPServer,
        sample_context: ContextEntry,
    ) -> None:
        """Test ask_deepseek error handling."""
        # Setup mock to raise ValueError
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(side_effect=ValueError("API key missing"))
        mock_deepseek_class.return_value = mock_client

        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Ask DeepSeek (should handle error)
        result = await mcp_server.call_tool("ask_deepseek", {"context_id": sample_context.id})

        assert result is not None
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_read_session_contexts_resource(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test reading contexts by session ID."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Read contexts for this session
        from pydantic import AnyUrl

        session_id = sample_context.session_id
        result = await mcp_server.read_resource(AnyUrl(f"mcp-toolz://contexts/session/{session_id}"))

        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_read_project_sessions_resource(self, mcp_server: ContextMCPServer, sample_context: ContextEntry) -> None:
        """Test reading project sessions."""
        # Save a context
        mcp_server.storage.save_context(sample_context)

        # Read sessions for this project
        with patch("os.getcwd", return_value=sample_context.project_path):
            from pydantic import AnyUrl

            result = await mcp_server.read_resource(AnyUrl("mcp-toolz://contexts/project/sessions"))

        assert result is not None
        assert isinstance(result, str)
