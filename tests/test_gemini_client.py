"""Tests for Google Gemini client."""

from unittest.mock import MagicMock, patch

import pytest

from context_manager.gemini_client import GeminiClient
from models import ContextEntry


class TestGeminiClient:
    """Test Gemini client."""

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_init(self, mock_model: MagicMock, mock_configure: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Gemini client initialization."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        client = GeminiClient()
        assert client is not None
        assert client.model_name == "gemini-2.0-flash-thinking-exp-01-21"
        mock_configure.assert_called_once_with(api_key="test-key")
        mock_model.assert_called_once()

    def test_init_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test initialization fails without API key."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="Google API key"):
            GeminiClient()

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_get_second_opinion(
        self, mock_model: MagicMock, mock_configure: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting a second opinion."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        # Mock Gemini response
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a solid implementation"
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        client = GeminiClient()
        response = client.get_second_opinion(sample_context)

        assert response == "This is a solid implementation"
        assert mock_instance.generate_content.called

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_get_second_opinion_with_question(
        self, mock_model: MagicMock, mock_configure: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test getting a second opinion with a custom question."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        # Mock Gemini response
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Yes, this approach is correct"
        mock_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_instance

        client = GeminiClient()
        response = client.get_second_opinion(sample_context, "Is this correct?")

        assert response == "Yes, this approach is correct"

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_format_context_for_gemini(
        self, mock_model: MagicMock, mock_configure: MagicMock, sample_context: ContextEntry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test formatting context for Gemini."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        client = GeminiClient()
        formatted = client._format_context_for_gemini(sample_context)

        assert "Test Context" in formatted
        assert sample_context.type in formatted
        assert "test.py" in formatted or "hello" in formatted

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_format_context_with_messages(self, mock_model: MagicMock, mock_configure: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with messages."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        context = ContextEntry(
            type="conversation",
            title="Test",
            content=ContextContent(messages=["Message 1", "Message 2"]),
            tags=[],
            project_path="/test",
        )

        client = GeminiClient()
        formatted = client._format_context_for_gemini(context)

        assert "Message 1" in formatted
        assert "Message 2" in formatted

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_format_context_with_suggestions(
        self, mock_model: MagicMock, mock_configure: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test formatting context with suggestions."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        context = ContextEntry(
            type="suggestion",
            title="Test",
            content=ContextContent(suggestions="Use dependency injection"),
            tags=[],
            project_path="/test",
        )

        client = GeminiClient()
        formatted = client._format_context_for_gemini(context)

        assert "Use dependency injection" in formatted

    @patch("context_manager.gemini_client.genai.configure")
    @patch("context_manager.gemini_client.genai.GenerativeModel")
    def test_format_context_with_errors(self, mock_model: MagicMock, mock_configure: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test formatting context with errors."""
        from models import ContextContent, ContextEntry

        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")

        context = ContextEntry(
            type="error",
            title="Test",
            content=ContextContent(errors="ValueError: invalid literal"),
            tags=[],
            project_path="/test",
        )

        client = GeminiClient()
        formatted = client._format_context_for_gemini(context)

        assert "ValueError: invalid literal" in formatted
