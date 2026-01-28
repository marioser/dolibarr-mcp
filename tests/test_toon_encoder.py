"""Tests for TOON (Token-Oriented Object Notation) encoder."""

import pytest
from datetime import datetime, date

from dolibarr_mcp.formats.toon_encoder import ToonEncoder, encode_toon, encode_response
from dolibarr_mcp.formats.formatter import (
    format_response,
    format_data,
    OutputFormat,
    get_format_from_request,
    compare_formats,
)


class TestToonEncoder:
    """Test TOON encoding functionality."""

    def test_encode_primitives(self):
        """Test encoding of primitive types."""
        encoder = ToonEncoder()

        assert encoder.encode(None) == "null"
        assert encoder.encode(True) == "true"
        assert encoder.encode(False) == "false"
        assert encoder.encode(42) == "42"
        assert encoder.encode(3.14) == "3.14"
        assert encoder.encode("hello") == "hello"

    def test_encode_string_quoting(self):
        """Test that strings with special chars are quoted."""
        encoder = ToonEncoder()

        # No quoting needed
        assert encoder.encode("simple") == "simple"
        assert encoder.encode("hello_world") == "hello_world"

        # Needs quoting
        assert encoder.encode("hello, world") == '"hello, world"'
        assert encoder.encode("has:colon") == '"has:colon"'
        assert encoder.encode("[brackets]") == '"[brackets]"'
        assert encoder.encode("true") == '"true"'  # Reserved word
        assert encoder.encode("123") == '"123"'  # Looks like number

    def test_encode_empty_string(self):
        """Test encoding of empty string."""
        encoder = ToonEncoder()
        assert encoder.encode("") == '""'

    def test_encode_dates(self):
        """Test encoding of date/datetime objects."""
        encoder = ToonEncoder()

        d = date(2024, 1, 15)
        assert encoder.encode(d) == "2024-01-15"

        dt = datetime(2024, 1, 15, 10, 30, 0)
        assert encoder.encode(dt) == "2024-01-15T10:30:00"

    def test_encode_uniform_list_tabular(self):
        """Test tabular encoding of uniform object lists."""
        encoder = ToonEncoder()

        data = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]

        result = encoder.encode(data)
        assert "[2]{id,name,email}:" in result
        assert "1,Alice,alice@example.com" in result
        assert "2,Bob,bob@example.com" in result

    def test_encode_non_uniform_list(self):
        """Test encoding of non-uniform lists."""
        encoder = ToonEncoder()

        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob", "extra": "field"},
        ]

        result = encoder.encode(data)
        # Should not use tabular format
        assert "- " in result

    def test_encode_dict(self):
        """Test YAML-like dict encoding."""
        encoder = ToonEncoder()

        data = {"name": "Test", "value": 42}
        result = encoder.encode(data)

        assert "name: Test" in result
        assert "value: 42" in result

    def test_encode_nested_dict(self):
        """Test encoding of nested dictionaries."""
        encoder = ToonEncoder()

        data = {
            "customer": {
                "id": 1,
                "name": "Test Corp"
            }
        }

        result = encoder.encode(data)
        assert "customer:" in result
        assert "id: 1" in result
        assert "name: Test Corp" in result


class TestEncodeResponse:
    """Test response encoding for MCP format."""

    def test_success_response(self):
        """Test encoding successful response."""
        response = {
            "success": True,
            "data": {"id": 1, "name": "Test"},
        }

        result = encode_response(response)
        assert "success: true" in result
        assert "data:" in result
        assert "id: 1" in result

    def test_error_response(self):
        """Test encoding error response."""
        response = {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Customer not found",
                "status": 404,
                "retriable": False,
            }
        }

        result = encode_response(response)
        assert "success: false" in result
        assert "error:" in result
        assert "NOT_FOUND" in result
        assert "no-retry" in result

    def test_paginated_response(self):
        """Test encoding paginated response with metadata."""
        response = {
            "success": True,
            "data": [
                {"id": 1, "name": "A"},
                {"id": 2, "name": "B"},
            ],
            "metadata": {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": 50,
                    "has_more": True,
                }
            }
        }

        result = encode_response(response)
        assert "success: true" in result
        assert "meta:" in result
        assert "limit=10" in result
        assert "total=50" in result
        assert "more=true" in result


class TestFormatter:
    """Test format selection and output formatting."""

    def test_format_response_toon(self):
        """Test TOON format output."""
        response = {"success": True, "data": {"id": 1}}
        result = format_response(response, OutputFormat.TOON)

        assert "success: true" in result
        assert "{" not in result  # No JSON braces

    def test_format_response_json(self):
        """Test JSON format output."""
        response = {"success": True, "data": {"id": 1}}
        result = format_response(response, OutputFormat.JSON)

        assert '"success": true' in result
        assert "{" in result

    def test_format_response_json_compact(self):
        """Test compact JSON format output."""
        response = {"success": True, "data": {"id": 1}}
        result = format_response(response, OutputFormat.JSON_COMPACT)

        assert '"success":true' in result
        assert "\n" not in result

    def test_default_format_is_toon(self):
        """Test that default format is TOON."""
        response = {"success": True, "data": 42}
        result = format_response(response)

        # TOON format
        assert "success: true" in result

    def test_get_format_from_request(self):
        """Test format extraction from request args."""
        assert get_format_from_request({"format": "json"}) == OutputFormat.JSON
        assert get_format_from_request({"format": "toon"}) == OutputFormat.TOON
        assert get_format_from_request({"output_format": "compact"}) == OutputFormat.JSON_COMPACT
        assert get_format_from_request({}) == OutputFormat.TOON  # default

    def test_compare_formats(self):
        """Test format comparison utility."""
        data = [
            {"id": 1, "name": "Test 1", "value": 100},
            {"id": 2, "name": "Test 2", "value": 200},
        ]

        result = compare_formats(data)

        assert "toon" in result
        assert "json" in result
        assert "json_compact" in result
        assert "savings" in result

        # TOON should be smaller than JSON
        assert result["toon"]["chars"] < result["json"]["chars"]


class TestEncodeToonFunction:
    """Test the convenience encode_toon function."""

    def test_encode_simple_data(self):
        """Test encoding simple data structures."""
        result = encode_toon({"name": "Test", "value": 42})
        assert "name: Test" in result
        assert "value: 42" in result

    def test_encode_list_data(self):
        """Test encoding list data."""
        result = encode_toon([1, 2, 3])
        assert "- 1" in result
        assert "- 2" in result
        assert "- 3" in result
