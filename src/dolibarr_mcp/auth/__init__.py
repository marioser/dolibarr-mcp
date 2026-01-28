"""Authentication module for Dolibarr MCP Server.

Provides API key authentication for securing MCP connections.
"""

from .api_key import (
    APIKeyAuth,
    verify_api_key,
    generate_api_key,
    require_auth,
)

__all__ = [
    "APIKeyAuth",
    "verify_api_key",
    "generate_api_key",
    "require_auth",
]
