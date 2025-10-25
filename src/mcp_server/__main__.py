"""Entry point for MCP server."""

import asyncio

from dotenv import load_dotenv

from mcp_server.server import ContextMCPServer

# Load environment variables
load_dotenv()


def main() -> None:
    """Main entry point."""
    server = ContextMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
