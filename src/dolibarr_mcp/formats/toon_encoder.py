"""TOON (Token-Oriented Object Notation) encoder for Dolibarr MCP.

TOON is a compact format optimized for LLM input, reducing token usage by ~40%
compared to JSON while maintaining readability.

Format specification: https://github.com/toon-format/toon
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


class ToonEncoder:
    """Encoder for TOON v3.0 format.

    TOON uses:
    - Tabular format for arrays of uniform objects: [N]{field1,field2}:
    - YAML-like indentation for nested objects
    - Minimal quoting (only when necessary)
    - Compact number representation
    """

    # Characters that require quoting in values
    SPECIAL_CHARS = re.compile(r'[,\[\]\{\}:\n\r\t]')

    # Pattern for values that look like numbers but should be strings
    NUMBER_PATTERN = re.compile(r'^-?\d+\.?\d*$')

    def __init__(self, indent: int = 2):
        """Initialize encoder.

        Args:
            indent: Number of spaces for indentation (default 2)
        """
        self.indent = indent

    def encode(self, data: Any) -> str:
        """Encode data to TOON format.

        Args:
            data: Data to encode (dict, list, or primitive)

        Returns:
            TOON-formatted string
        """
        if data is None:
            return "null"

        if isinstance(data, bool):
            return "true" if data else "false"

        if isinstance(data, (int, float, Decimal)):
            return self._encode_number(data)

        if isinstance(data, str):
            return self._encode_string(data)

        if isinstance(data, (datetime, date)):
            return data.isoformat()

        if isinstance(data, list):
            return self._encode_list(data)

        if isinstance(data, dict):
            return self._encode_dict(data)

        # Fallback for unknown types
        return self._encode_string(str(data))

    def _encode_number(self, value: Union[int, float, Decimal]) -> str:
        """Encode number with minimal representation."""
        if isinstance(value, float):
            # Remove trailing zeros
            formatted = f"{value:g}"
            return formatted
        if isinstance(value, Decimal):
            # Normalize to remove trailing zeros
            return str(value.normalize())
        return str(value)

    def _encode_string(self, value: str) -> str:
        """Encode string, quoting only when necessary."""
        if not value:
            return '""'

        # Check if quoting is needed
        needs_quotes = (
            self.SPECIAL_CHARS.search(value) is not None or
            value.startswith((' ', '\t')) or
            value.endswith((' ', '\t')) or
            value in ('true', 'false', 'null') or
            self.NUMBER_PATTERN.match(value)
        )

        if needs_quotes:
            # Escape quotes and backslashes
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'

        return value

    def _encode_list(self, items: List[Any], level: int = 0) -> str:
        """Encode list, using tabular format for uniform objects."""
        if not items:
            return "[]"

        # Check if all items are uniform dicts (same keys)
        if self._is_uniform_dict_list(items):
            return self._encode_tabular(items, level)

        # Non-uniform list - use standard format
        lines = []
        for item in items:
            if isinstance(item, dict):
                encoded = self._encode_dict(item, level + 1)
                lines.append(f"{self._indent(level)}- {encoded.lstrip()}")
            else:
                lines.append(f"{self._indent(level)}- {self.encode(item)}")

        return '\n'.join(lines)

    def _is_uniform_dict_list(self, items: List[Any]) -> bool:
        """Check if all items are dicts with identical keys."""
        if not items or not isinstance(items[0], dict):
            return False

        first_keys = set(items[0].keys())
        return all(
            isinstance(item, dict) and set(item.keys()) == first_keys
            for item in items
        )

    def _encode_tabular(self, items: List[Dict], level: int = 0) -> str:
        """Encode uniform dict list as TOON tabular format.

        Format: [N]{field1,field2}:
                value1,value2
                value3,value4
        """
        if not items:
            return "[]"

        fields = list(items[0].keys())
        header = f"[{len(items)}]{{{','.join(fields)}}}:"

        rows = []
        for item in items:
            values = []
            for field in fields:
                value = item.get(field)
                encoded = self._encode_value_for_table(value)
                values.append(encoded)
            rows.append(','.join(values))

        indent = self._indent(level)
        if level > 0:
            # Indented tabular
            lines = [f"{indent}{header}"]
            for row in rows:
                lines.append(f"{indent}{row}")
            return '\n'.join(lines)
        else:
            return header + '\n' + '\n'.join(rows)

    def _encode_value_for_table(self, value: Any) -> str:
        """Encode a value for use in tabular row (no newlines allowed)."""
        if value is None:
            return ""

        if isinstance(value, bool):
            return "true" if value else "false"

        if isinstance(value, (int, float, Decimal)):
            return self._encode_number(value)

        if isinstance(value, str):
            # For tables, always escape commas
            if ',' in value or '\n' in value or '"' in value:
                escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                return f'"{escaped}"'
            return value

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, (list, dict)):
            # Nested structures in tables - use compact JSON-like
            return self._encode_nested_compact(value)

        return str(value)

    def _encode_nested_compact(self, value: Any) -> str:
        """Encode nested structure compactly for table cells."""
        if isinstance(value, list):
            if not value:
                return "[]"
            items = [self._encode_value_for_table(v) for v in value]
            return f"[{';'.join(items)}]"

        if isinstance(value, dict):
            if not value:
                return "{}"
            pairs = [f"{k}:{self._encode_value_for_table(v)}" for k, v in value.items()]
            return f"{{{';'.join(pairs)}}}"

        return self._encode_value_for_table(value)

    def _encode_dict(self, obj: Dict, level: int = 0) -> str:
        """Encode dict with YAML-like indentation."""
        if not obj:
            return "{}"

        lines = []
        indent = self._indent(level)

        for key, value in obj.items():
            if isinstance(value, dict):
                if value:
                    lines.append(f"{indent}{key}:")
                    nested = self._encode_dict(value, level + 1)
                    lines.append(nested)
                else:
                    lines.append(f"{indent}{key}: {{}}")
            elif isinstance(value, list):
                if value and self._is_uniform_dict_list(value):
                    lines.append(f"{indent}{key}:")
                    tabular = self._encode_tabular(value, level + 1)
                    lines.append(tabular)
                elif value:
                    lines.append(f"{indent}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"{self._indent(level + 1)}-")
                            nested = self._encode_dict(item, level + 2)
                            lines.append(nested)
                        else:
                            lines.append(f"{self._indent(level + 1)}- {self.encode(item)}")
                else:
                    lines.append(f"{indent}{key}: []")
            else:
                encoded_value = self.encode(value)
                lines.append(f"{indent}{key}: {encoded_value}")

        return '\n'.join(lines)

    def _indent(self, level: int) -> str:
        """Get indentation string for given level."""
        return ' ' * (self.indent * level)


def encode_toon(data: Any, indent: int = 2) -> str:
    """Convenience function to encode data as TOON.

    Args:
        data: Data to encode
        indent: Indentation level (default 2)

    Returns:
        TOON-formatted string
    """
    encoder = ToonEncoder(indent=indent)
    return encoder.encode(data)


def encode_response(response: Dict[str, Any]) -> str:
    """Encode a standard MCP response to TOON format.

    Handles the standard response structure:
    {success: bool, data: Any, metadata?: Dict, error?: Dict}

    Args:
        response: Standard response dict

    Returns:
        TOON-formatted string
    """
    encoder = ToonEncoder()

    lines = []

    # Success flag
    lines.append(f"success: {'true' if response.get('success') else 'false'}")

    # Data section
    if 'data' in response:
        data = response['data']
        if isinstance(data, list) and encoder._is_uniform_dict_list(data):
            lines.append("data:")
            lines.append(encoder._encode_tabular(data, level=1))
        elif isinstance(data, dict):
            lines.append("data:")
            lines.append(encoder._encode_dict(data, level=1))
        else:
            lines.append(f"data: {encoder.encode(data)}")

    # Metadata section (compact)
    if 'metadata' in response and response['metadata']:
        meta = response['metadata']
        if 'pagination' in meta:
            p = meta['pagination']
            lines.append(f"meta: limit={p.get('limit', 0)},offset={p.get('offset', 0)},total={p.get('total', 0)},more={'true' if p.get('has_more') else 'false'}")
        else:
            lines.append("meta:")
            lines.append(encoder._encode_dict(meta, level=1))

    # Error section
    if 'error' in response:
        err = response['error']
        lines.append(f"error: {err.get('code', 'UNKNOWN')}|{err.get('message', '')}|{err.get('status', 500)}|{'retry' if err.get('retriable') else 'no-retry'}")

    return '\n'.join(lines)
