"""Tests for Anthropic client."""

from unittest.mock import MagicMock, patch

import pytest
from anthropic.types import TextBlock

from context_manager.anthropic_client import ClaudeClient
from models import ContextEntry


class TestClaudeClient:
    """Test Claude client."""

    @patch("context_manager.anthropic_client.Anthropic")
    def test_init(self, mock_anthropic: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Claude client initialization."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        client = ClaudeClient()
        assert client is not None
        assert client.model == "claude-sonnet-4-5-20250929"
        mock_anthropic.assert_called_once()

    def test_init_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization fails without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError, match="Anthropic API key"):
            ClaudeClient()

    @patch("context_manager.anthropic_client.Anthropic")
    def test_get_second_opinion(self, mock_anthropic: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting a second opinion."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Mock Anthropic response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "This looks good to me"
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        response = client.get_second_opinion(sample_context)

        assert response == "This looks good to me"
        assert mock_client.messages.create.called

    @patch("context_manager.anthropic_client.Anthropic")
    def test_get_second_opinion_with_question(
        self, mock_anthropic: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting a second opinion with a custom question."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Mock Anthropic response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_text_block = MagicMock(spec=TextBlock)
        mock_text_block.text = "Yes, that's correct"
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()
        response = client.get_second_opinion(sample_context, "Is this right?")

        assert response == "Yes, that's correct"

    @patch("context_manager.anthropic_client.Anthropic")
    def test_format_context_for_claude(
        self, mock_anthropic: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test formatting context for Claude."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        mock_anthropic.return_value = MagicMock()

        client = ClaudeClient()
        formatted = client._format_context_for_claude(sample_context)

        assert "Test Context" in formatted
        assert sample_context.type in formatted
        assert "test.py" in formatted or "hello" in formatted

    @patch("context_manager.anthropic_client.Anthropic")
    def test_format_context_with_messages(self, mock_anthropic: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with messages."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        mock_anthropic.return_value = MagicMock()

        context = ContextEntry(
            type="conversation",
            title="Test",
            content=ContextContent(messages=["Message 1", "Message 2"]),
            tags=[],
            project_path="/test",
        )

        client = ClaudeClient()
        formatted = client._format_context_for_claude(context)

        assert "Message 1" in formatted
        assert "Message 2" in formatted

    @patch("context_manager.anthropic_client.Anthropic")
    def test_format_context_with_suggestions(self, mock_anthropic: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with suggestions."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        mock_anthropic.return_value = MagicMock()

        context = ContextEntry(
            type="suggestion",
            title="Test",
            content=ContextContent(suggestions="Use type hints"),
            tags=[],
            project_path="/test",
        )

        client = ClaudeClient()
        formatted = client._format_context_for_claude(context)

        assert "Use type hints" in formatted

    @patch("context_manager.anthropic_client.Anthropic")
    def test_format_context_with_errors(self, mock_anthropic: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with errors."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        mock_anthropic.return_value = MagicMock()

        context = ContextEntry(
            type="error",
            title="Test",
            content=ContextContent(errors="TypeError: expected str"),
            tags=[],
            project_path="/test",
        )

        client = ClaudeClient()
        formatted = client._format_context_for_claude(context)

        assert "TypeError: expected str" in formatted
