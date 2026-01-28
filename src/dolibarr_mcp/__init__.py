"""
Dolibarr MCP Server Package

Professional Model Context Protocol server for complete Dolibarr ERP/CRM management.
Optimized for universal AI agent compatibility with reduced token usage.
"""

__version__ = "2.0.0"
__author__ = "Dolibarr MCP Team"

# New modular imports
from .client import DolibarrClient, DolibarrAPIError, DolibarrValidationError
from .config import Config

# Legacy compatibility - import from old location if new doesn't exist
try:
    from .client import DolibarrClient
except ImportError:
    from .dolibarr_client import DolibarrClient

__all__ = [
    "DolibarrClient",
    "DolibarrAPIError",
    "DolibarrValidationError",
    "Config",
]
