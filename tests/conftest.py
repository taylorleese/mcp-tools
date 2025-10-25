"""Shared pytest fixtures for all tests."""

import os
import tempfile
from collections.abc import AsyncGenerator, Generator
from datetime import UTC
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from context_manager.anthropic_client import ClaudeClient
from context_manager.openai_client import ChatGPTClient
from context_manager.storage import ContextStorage
from models import ContextContent, ContextEntry, Todo, TodoListSnapshot


@pytest.fixture
def temp_db_path() -> Generator[str]:
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest_asyncio.fixture
async def storage(temp_db_path: str) -> AsyncGenerator[ContextStorage]:
    """Create a ContextStorage instance with a temporary database."""
    store = ContextStorage(temp_db_path)
    yield store
    store.close()


@pytest.fixture
def sample_context() -> ContextEntry:
    """Create a sample context entry for testing."""
    from datetime import datetime

    return ContextEntry(
        type="code",
        title="Test Context",
        content=ContextContent(code={"test.py": "print('hello')"}),
        tags=["test", "sample"],
        project_path="/test/project",
        session_id="test-session-123",
        session_timestamp=datetime.now(UTC),
    )


@pytest.fixture
def sample_todo_snapshot() -> TodoListSnapshot:
    """Create a sample todo snapshot for testing."""
    return TodoListSnapshot(
        todos=[
            Todo(content="Task 1", status="pending", activeForm="Doing task 1"),
            Todo(content="Task 2", status="in_progress", activeForm="Doing task 2"),
            Todo(content="Task 3", status="completed", activeForm="Doing task 3"),
        ],
        context="Testing todos",
        project_path="/test/project",
        is_active=True,
    )


@pytest.fixture
def mock_openai_client() -> ChatGPTClient:
    """Create a mock OpenAI client for testing."""
    client = MagicMock(spec=ChatGPTClient)
    client.query = AsyncMock(return_value="This is a mocked ChatGPT response")
    return client


@pytest.fixture
def mock_anthropic_client() -> ClaudeClient:
    """Create a mock Anthropic client for testing."""
    client = MagicMock(spec=ClaudeClient)
    client.query = AsyncMock(return_value="This is a mocked Claude response")
    return client


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("MCP_TOOLZ_MODEL", "gpt-5")
    monkeypatch.setenv("MCP_TOOLZ_CLAUDE_MODEL", "claude-sonnet-4-5-20250929")


@pytest.fixture
def project_path(tmp_path: Path) -> str:
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return str(project_dir)
