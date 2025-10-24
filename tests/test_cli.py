"""Tests for CLI commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from context_manager.cli import main
from models import ContextEntry, TodoListSnapshot


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_storage(temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock storage for CLI tests."""
    monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
    return MagicMock()


class TestContextCommands:
    """Test context CLI commands."""

    def test_context_save_with_content(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test saving context with inline content."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(
            main,
            [
                "context",
                "save",
                "--type",
                "code",
                "--title",
                "Test Context",
                "--content",
                "def hello(): pass",
                "--tags",
                "python,test",
            ],
        )

        assert result.exit_code == 0
        assert "Context saved" in result.output
        assert "ID:" in result.output

    def test_context_save_with_file(
        self, cli_runner: CliRunner, temp_db_path: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test saving context from file."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # Create temporary file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        result = cli_runner.invoke(
            main,
            ["context", "save", "--type", "code", "--title", "From File", "--file", str(test_file)],
        )

        assert result.exit_code == 0
        assert "Context saved" in result.output

    def test_context_save_missing_content(self, cli_runner: CliRunner) -> None:
        """Test saving context without content or file."""
        result = cli_runner.invoke(
            main,
            ["context", "save", "--type", "code", "--title", "No Content"],
        )

        assert result.exit_code == 1
        assert "Either --content or --file must be provided" in result.output

    def test_context_list(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing contexts."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # First save a context
        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "list"])

        assert result.exit_code == 0
        assert "Test Context" in result.output

    def test_context_list_with_type_filter(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing contexts with type filter."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "list", "--type", "code"])

        assert result.exit_code == 0

    def test_context_search(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test searching contexts."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "search", "test"])

        assert result.exit_code == 0

    def test_context_show(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test showing a specific context."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "show", sample_context.id])

        assert result.exit_code == 0
        assert "Test Context" in result.output

    def test_context_show_not_found(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test showing a non-existent context."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["context", "show", "nonexistent-id"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_context_show_output(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test showing context output format."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "show", sample_context.id])

        assert result.exit_code == 0
        assert "Test Context" in result.output
        assert "Type:" in result.output

    def test_context_delete(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test deleting a context."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "delete", sample_context.id], input="y\n")

        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_context_delete_cancelled(
        self, cli_runner: CliRunner, temp_db_path: str, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test cancelling context deletion."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        result = cli_runner.invoke(main, ["context", "delete", sample_context.id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    @patch("context_manager.cli.ChatGPTClient")
    def test_context_save_and_query(
        self,
        mock_chatgpt_class: MagicMock,
        cli_runner: CliRunner,
        temp_db_path: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test save-and-query command."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # Mock ChatGPT client
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked response")
        mock_chatgpt_class.return_value = mock_client

        result = cli_runner.invoke(
            main,
            [
                "context",
                "save-and-query",
                "--type",
                "code",
                "--title",
                "Test",
                "--content",
                "test content",
            ],
        )

        assert result.exit_code == 0
        assert "Context saved" in result.output

    @patch("context_manager.cli.ChatGPTClient")
    def test_context_ask_chatgpt(
        self,
        mock_chatgpt_class: MagicMock,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_context: ContextEntry,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test ask-chatgpt command."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # Save context first
        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        # Mock ChatGPT client
        mock_client = MagicMock()
        mock_client.query_context = MagicMock(return_value="Mocked response")
        mock_chatgpt_class.return_value = mock_client

        result = cli_runner.invoke(
            main,
            ["context", "ask-chatgpt", sample_context.id, "--question", "What is this?"],
        )

        assert result.exit_code == 0

    @patch("context_manager.anthropic_client.ClaudeClient")
    def test_context_ask_claude(
        self,
        mock_claude_class: MagicMock,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_context: ContextEntry,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test ask-claude command."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # Save context first
        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_context(sample_context)

        # Mock Claude client
        mock_client = MagicMock()
        mock_client.get_second_opinion = MagicMock(return_value="Mocked response")
        mock_claude_class.return_value = mock_client

        result = cli_runner.invoke(
            main,
            ["context", "ask-claude", sample_context.id, "--question", "What is this?"],
        )

        assert result.exit_code == 0


class TestTodoCommands:
    """Test todo CLI commands."""

    def test_todo_save(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test saving todos."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        # Create todos JSON
        todos_data = [
            {"content": "Task 1", "status": "pending", "activeForm": "Doing task 1"},
            {"content": "Task 2", "status": "in_progress", "activeForm": "Doing task 2"},
        ]

        result = cli_runner.invoke(
            main,
            ["todo", "save", "--todos", json.dumps(todos_data), "--context", "Test todos"],
        )

        assert result.exit_code == 0
        assert "saved" in result.output

    def test_todo_save_missing_file(self, cli_runner: CliRunner) -> None:
        """Test saving todos without file."""
        result = cli_runner.invoke(main, ["todo", "save"])

        assert result.exit_code != 0

    def test_todo_list(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test listing todo snapshots."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "list"])

        assert result.exit_code == 0
        assert "snapshots" in result.output or "Task" in result.output

    def test_todo_show(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test showing a todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "show", sample_todo_snapshot.id])

        assert result.exit_code == 0
        assert "Task 1" in result.output

    def test_todo_show_output(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test showing todo snapshot output format."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "show", sample_todo_snapshot.id])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Snapshot ID" in result.output

    def test_todo_restore(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test restoring a todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "restore", sample_todo_snapshot.id])

        assert result.exit_code == 0
        assert "Task 1" in result.output

    def test_todo_search(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test searching todo snapshots."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "search", "Task"])

        assert result.exit_code == 0

    def test_todo_delete(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test deleting a todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "delete", sample_todo_snapshot.id], input="y\n")

        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_todo_delete_cancelled(
        self,
        cli_runner: CliRunner,
        temp_db_path: str,
        sample_todo_snapshot: TodoListSnapshot,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test cancelling todo deletion."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        from context_manager.storage import ContextStorage

        storage = ContextStorage(temp_db_path)
        storage.save_todo_snapshot(sample_todo_snapshot)

        result = cli_runner.invoke(main, ["todo", "delete", sample_todo_snapshot.id], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output

    def test_todo_save_invalid_json(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test saving todos with invalid JSON."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["todo", "save", "--todos", "not-valid-json"])

        assert result.exit_code == 1
        assert "Invalid todos JSON" in result.output

    def test_todo_show_not_found(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test showing non-existent todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["todo", "show", "nonexistent-id"])

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_todo_delete_not_found(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test deleting non-existent todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["todo", "delete", "nonexistent-id"])

        assert result.exit_code == 1

    def test_context_list_empty(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing contexts when empty."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["context", "list"])

        assert result.exit_code == 0

    def test_context_search_no_results(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test searching contexts with no results."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["context", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No contexts found" in result.output

    def test_todo_search_no_results(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test searching todos with no results."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["todo", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No todo snapshots found" in result.output

    def test_todo_restore_not_found(self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test restoring non-existent todo snapshot."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(main, ["todo", "restore", "nonexistent-id"])

        assert result.exit_code == 1

    @patch("context_manager.cli.ChatGPTClient")
    def test_context_save_and_query_with_file(
        self, mock_client: MagicMock, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Test save-and-query with file path."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Create temp file
        content_file = tmp_path / "content.txt"
        content_file.write_text("def test(): pass")

        # Mock ChatGPT response
        mock_instance = MagicMock()
        mock_instance.get_second_opinion.return_value = "Looks good"
        mock_client.return_value = mock_instance

        result = cli_runner.invoke(
            main,
            [
                "context",
                "save-and-query",
                "--type",
                "code",
                "--title",
                "Test",
                "--file",
                str(content_file),
            ],
        )

        assert result.exit_code == 0
        assert "Looks good" in result.output

    def test_context_save_and_query_missing_content(
        self, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test save-and-query without content or file."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)

        result = cli_runner.invoke(
            main,
            ["context", "save-and-query", "--type", "code", "--title", "Test"],
        )

        assert result.exit_code == 1
        assert "Either --content or --file must be provided" in result.output

    @patch("context_manager.cli.ChatGPTClient")
    def test_context_save_and_query_chatgpt_error(
        self, mock_client: MagicMock, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test save-and-query with ChatGPT error."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock ChatGPT error
        mock_instance = MagicMock()
        mock_instance.get_second_opinion.side_effect = Exception("API error")
        mock_client.return_value = mock_instance

        result = cli_runner.invoke(
            main,
            [
                "context",
                "save-and-query",
                "--type",
                "code",
                "--title",
                "Test",
                "--content",
                "test code",
            ],
        )

        assert result.exit_code == 1
        assert "Error querying ChatGPT" in result.output

    @patch("context_manager.anthropic_client.ClaudeClient")
    def test_context_ask_claude_error(
        self, mock_client: MagicMock, cli_runner: CliRunner, temp_db_path: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test ask-claude with Claude error."""
        monkeypatch.setenv("MCP_TOOLZ_DB_PATH", temp_db_path)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # First save a context
        result = cli_runner.invoke(
            main,
            ["context", "save", "--type", "code", "--title", "Test", "--content", "test"],
        )
        # Extract context ID (remove trailing parenthesis)
        context_id = result.output.split("ID: ")[1].split(")")[0].strip()

        # Mock Claude error
        mock_instance = MagicMock()
        mock_instance.get_second_opinion.side_effect = Exception("API error")
        mock_client.return_value = mock_instance

        result = cli_runner.invoke(main, ["context", "ask-claude", context_id])

        assert result.exit_code == 1
        assert "Error querying Claude" in result.output
