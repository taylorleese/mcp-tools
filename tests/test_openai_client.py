"""Tests for OpenAI client."""

from unittest.mock import MagicMock, patch

import pytest

from context_manager.openai_client import ChatGPTClient
from models import ContextEntry


class TestChatGPTClient:
    """Test ChatGPT client."""

    @patch("context_manager.openai_client.OpenAI")
    def test_init(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test ChatGPT client initialization."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        client = ChatGPTClient()
        assert client is not None
        assert client.model == "gpt-5"
        mock_openai.assert_called_once()

    def test_init_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization fails without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OpenAI API key"):
            ChatGPTClient()

    @patch("context_manager.openai_client.OpenAI")
    def test_get_second_opinion(self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting a second opinion."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a good approach"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = ChatGPTClient()
        response = client.get_second_opinion(sample_context)

        assert response == "This is a good approach"
        assert mock_client.chat.completions.create.called

    @patch("context_manager.openai_client.OpenAI")
    def test_get_second_opinion_with_question(
        self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting a second opinion with a custom question."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Yes, this is correct"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = ChatGPTClient()
        response = client.get_second_opinion(sample_context, "Is this correct?")

        assert response == "Yes, this is correct"

    @patch("context_manager.openai_client.OpenAI")
    def test_format_context_for_chatgpt(
        self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test formatting context for ChatGPT."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        client = ChatGPTClient()
        formatted = client._format_context_for_chatgpt(sample_context)

        assert "Test Context" in formatted
        assert sample_context.type in formatted
        assert "test.py" in formatted or "hello" in formatted

    @patch("context_manager.openai_client.OpenAI")
    def test_format_context_with_messages(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with messages."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="conversation",
            title="Test",
            content=ContextContent(messages=["Message 1", "Message 2"]),
            tags=[],
            project_path="/test",
        )

        client = ChatGPTClient()
        formatted = client._format_context_for_chatgpt(context)

        assert "Message 1" in formatted
        assert "Message 2" in formatted

    @patch("context_manager.openai_client.OpenAI")
    def test_format_context_with_suggestions(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with suggestions."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="suggestion",
            title="Test",
            content=ContextContent(suggestions="Use async/await"),
            tags=[],
            project_path="/test",
        )

        client = ChatGPTClient()
        formatted = client._format_context_for_chatgpt(context)

        assert "Use async/await" in formatted

    @patch("context_manager.openai_client.OpenAI")
    def test_format_context_with_errors(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with errors."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="error",
            title="Test",
            content=ContextContent(errors="SyntaxError: line 10"),
            tags=[],
            project_path="/test",
        )

        client = ChatGPTClient()
        formatted = client._format_context_for_chatgpt(context)

        assert "SyntaxError: line 10" in formatted
