"""Response formatter with TOON/JSON format selection.

TOON is the default format for optimal token efficiency (~40% reduction).
JSON is available as fallback when explicitly requested or when TOON encoding fails.
"""

import json
import logging
from enum import Enum
from typing import Any, Dict, Optional, Union

from .toon_encoder import ToonEncoder, encode_response as encode_toon_response

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Supported output formats."""
    TOON = "toon"      # Default - Token-Oriented Object Notation
    JSON = "json"      # Fallback - Standard JSON
    JSON_COMPACT = "json_compact"  # Minified JSON (no whitespace)


# Default format for responses
DEFAULT_FORMAT = OutputFormat.TOON


def format_response(
    response: Dict[str, Any],
    format: Optional[OutputFormat] = None,
    fallback_to_json: bool = True
) -> str:
    """Format a response in the specified format.

    Args:
        response: Response dict to format
        format: Output format (default: TOON)
        fallback_to_json: If True, fall back to JSON on TOON encoding errors

    Returns:
        Formatted string
    """
    output_format = format or DEFAULT_FORMAT

    if output_format == OutputFormat.JSON:
        return json.dumps(response, default=str, indent=2)

    if output_format == OutputFormat.JSON_COMPACT:
        return json.dumps(response, default=str, separators=(',', ':'))

    # TOON format (default)
    try:
        return encode_toon_response(response)
    except Exception as e:
        if fallback_to_json:
            logger.warning(f"TOON encoding failed, falling back to JSON: {e}")
            return json.dumps(response, default=str, indent=2)
        raise


def format_data(
    data: Any,
    format: Optional[OutputFormat] = None,
    fallback_to_json: bool = True
) -> str:
    """Format raw data (not wrapped in response structure).

    Args:
        data: Data to format
        format: Output format (default: TOON)
        fallback_to_json: If True, fall back to JSON on TOON encoding errors

    Returns:
        Formatted string
    """
    output_format = format or DEFAULT_FORMAT

    if output_format == OutputFormat.JSON:
        return json.dumps(data, default=str, indent=2)

    if output_format == OutputFormat.JSON_COMPACT:
        return json.dumps(data, default=str, separators=(',', ':'))

    # TOON format (default)
    try:
        encoder = ToonEncoder()
        return encoder.encode(data)
    except Exception as e:
        if fallback_to_json:
            logger.warning(f"TOON encoding failed, falling back to JSON: {e}")
            return json.dumps(data, default=str, indent=2)
        raise


def get_format_from_request(
    args: Dict[str, Any],
    default: OutputFormat = DEFAULT_FORMAT
) -> OutputFormat:
    """Extract output format from request arguments.

    Checks for 'format' or 'output_format' in args.

    Args:
        args: Request arguments dict
        default: Default format if not specified

    Returns:
        OutputFormat enum value
    """
    format_str = args.get('format') or args.get('output_format')

    if not format_str:
        return default

    format_str = format_str.lower().strip()

    if format_str in ('toon', 'token'):
        return OutputFormat.TOON
    elif format_str == 'json':
        return OutputFormat.JSON
    elif format_str in ('json_compact', 'compact', 'minified'):
        return OutputFormat.JSON_COMPACT

    logger.warning(f"Unknown format '{format_str}', using default")
    return default


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses rough approximation: ~4 characters per token for English/code.

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    return len(text) // 4


def compare_formats(data: Any) -> Dict[str, Any]:
    """Compare token usage between formats.

    Useful for debugging and optimization.

    Args:
        data: Data to format

    Returns:
        Dict with format comparisons
    """
    toon_text = format_data(data, OutputFormat.TOON)
    json_text = format_data(data, OutputFormat.JSON)
    json_compact_text = format_data(data, OutputFormat.JSON_COMPACT)

    toon_tokens = estimate_tokens(toon_text)
    json_tokens = estimate_tokens(json_text)
    json_compact_tokens = estimate_tokens(json_compact_text)

    return {
        "toon": {
            "chars": len(toon_text),
            "tokens": toon_tokens,
        },
        "json": {
            "chars": len(json_text),
            "tokens": json_tokens,
        },
        "json_compact": {
            "chars": len(json_compact_text),
            "tokens": json_compact_tokens,
        },
        "savings": {
            "toon_vs_json": f"{(1 - toon_tokens / json_tokens) * 100:.1f}%" if json_tokens > 0 else "N/A",
            "toon_vs_compact": f"{(1 - toon_tokens / json_compact_tokens) * 100:.1f}%" if json_compact_tokens > 0 else "N/A",
        }
    }
