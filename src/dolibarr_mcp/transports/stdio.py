"""STDIO transport for MCP server.

This module handles communication over standard input/output,
which is the default transport for Claude Desktop integration.
"""

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server


async def run_stdio_server(server: Server, version: str = "2.0.0") -> None:
    """Run MCP server over STDIO transport.

    This is the default transport for Claude Desktop and other
    MCP clients that communicate via stdin/stdout.

    Args:
        server: The MCP Server instance
        version: Server version string
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dolibarr-mcp",
                server_version=version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
