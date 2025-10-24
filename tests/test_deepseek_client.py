"""Tests for DeepSeek client."""

from unittest.mock import MagicMock, patch

import pytest

from context_manager.deepseek_client import DeepSeekClient
from models import ContextEntry


class TestDeepSeekClient:
    """Test DeepSeek client."""

    @patch("context_manager.deepseek_client.OpenAI")
    def test_init(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test DeepSeek client initialization."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        client = DeepSeekClient()
        assert client is not None
        assert client.model == "deepseek-chat"
        # Verify OpenAI client was initialized with DeepSeek base URL
        mock_openai.assert_called_once_with(api_key="test-key", base_url="https://api.deepseek.com")

    def test_init_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization fails without API key."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError, match="DeepSeek API key"):
            DeepSeekClient()

    @patch("context_manager.deepseek_client.OpenAI")
    def test_get_second_opinion(self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting a second opinion."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

        # Mock DeepSeek response (OpenAI-compatible)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This code looks efficient"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = DeepSeekClient()
        response = client.get_second_opinion(sample_context)

        assert response == "This code looks efficient"
        assert mock_client.chat.completions.create.called

    @patch("context_manager.deepseek_client.OpenAI")
    def test_get_second_opinion_with_question(
        self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting a second opinion with a custom question."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

        # Mock DeepSeek response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Yes, the implementation is optimal"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = DeepSeekClient()
        response = client.get_second_opinion(sample_context, "Is this optimal?")

        assert response == "Yes, the implementation is optimal"

    @patch("context_manager.deepseek_client.OpenAI")
    def test_format_context_for_deepseek(
        self, mock_openai: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test formatting context for DeepSeek."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        client = DeepSeekClient()
        formatted = client._format_context_for_deepseek(sample_context)

        assert "Test Context" in formatted
        assert sample_context.type in formatted
        assert "test.py" in formatted or "hello" in formatted

    @patch("context_manager.deepseek_client.OpenAI")
    def test_format_context_with_messages(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with messages."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="conversation",
            title="Test",
            content=ContextContent(messages=["Message 1", "Message 2"]),
            tags=[],
            project_path="/test",
        )

        client = DeepSeekClient()
        formatted = client._format_context_for_deepseek(context)

        assert "Message 1" in formatted
        assert "Message 2" in formatted

    @patch("context_manager.deepseek_client.OpenAI")
    def test_format_context_with_suggestions(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with suggestions."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="suggestion",
            title="Test",
            content=ContextContent(suggestions="Implement caching layer"),
            tags=[],
            project_path="/test",
        )

        client = DeepSeekClient()
        formatted = client._format_context_for_deepseek(context)

        assert "Implement caching layer" in formatted

    @patch("context_manager.deepseek_client.OpenAI")
    def test_format_context_with_errors(self, mock_openai: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with errors."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
        mock_openai.return_value = MagicMock()

        context = ContextEntry(
            type="error",
            title="Test",
            content=ContextContent(errors="IndexError: list index out of range"),
            tags=[],
            project_path="/test",
        )

        client = DeepSeekClient()
        formatted = client._format_context_for_deepseek(context)

        assert "IndexError: list index out of range" in formatted
