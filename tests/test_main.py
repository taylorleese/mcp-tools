"""Tests for __main__ entry points."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.integration
class TestMCPServerMain:
    """Test MCP server __main__ entry point."""

    @patch("mcp_server.__main__.ContextMCPServer")
    @patch("mcp_server.__main__.asyncio.run")
    def test_mcp_server_main(self, mock_asyncio_run: MagicMock, mock_server_class: MagicMock) -> None:
        """Test that mcp_server.__main__ main() function runs the server."""
        from mcp_server.__main__ import main

        # Mock the server instance
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server

        # Call the main function
        main()

        # Verify server was created and run
        mock_server_class.assert_called_once()
        mock_asyncio_run.assert_called_once_with(mock_server.run())
