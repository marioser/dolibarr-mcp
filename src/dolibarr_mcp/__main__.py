"""Main entry point for Dolibarr MCP server."""

import sys
import asyncio

from .dolibarr_mcp_server import main


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}", file=sys.stderr)
        sys.exit(1)
