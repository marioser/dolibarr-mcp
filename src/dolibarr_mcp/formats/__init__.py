"""Output format module for Dolibarr MCP.

Supports TOON (Token-Oriented Object Notation) and JSON formats.
TOON is the default format for optimal token efficiency.
"""

from .toon_encoder import ToonEncoder, encode_toon
from .formatter import (
    format_response,
    OutputFormat,
    get_format_from_request,
)

__all__ = [
    "ToonEncoder",
    "encode_toon",
    "format_response",
    "OutputFormat",
    "get_format_from_request",
]
