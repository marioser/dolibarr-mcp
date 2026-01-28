"""Tests for API Key authentication module."""

import pytest
import time
from unittest.mock import MagicMock

from src.dolibarr_mcp.auth.api_key import (
    APIKeyAuth,
    generate_api_key,
    verify_api_key,
    extract_bearer_token,
)


class TestAPIKeyGeneration:
    """Tests for API key generation."""

    def test_generate_key_default_length(self):
        """Generate key with default length (32 bytes = 64 hex chars)."""
        key = generate_api_key()
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_generate_key_custom_length(self):
        """Generate key with custom length."""
        key = generate_api_key(length=16)
        assert len(key) == 32

    def test_generate_unique_keys(self):
        """Each generated key should be unique."""
        keys = [generate_api_key() for _ in range(100)]
        assert len(set(keys)) == 100


class TestBearerTokenExtraction:
    """Tests for bearer token extraction from Authorization header."""

    def test_extract_valid_bearer(self):
        """Extract token from valid Bearer header."""
        token = extract_bearer_token("Bearer abc123")
        assert token == "abc123"

    def test_extract_bearer_case_insensitive(self):
        """Bearer keyword should be case-insensitive."""
        token = extract_bearer_token("bearer abc123")
        assert token == "abc123"

        token = extract_bearer_token("BEARER abc123")
        assert token == "abc123"

    def test_extract_empty_header(self):
        """Return None for empty header."""
        token = extract_bearer_token("")
        assert token is None

    def test_extract_none_header(self):
        """Return None for None header."""
        token = extract_bearer_token(None)
        assert token is None

    def test_extract_invalid_format(self):
        """Return None for non-Bearer auth."""
        token = extract_bearer_token("Basic abc123")
        assert token is None

    def test_extract_no_token(self):
        """Return None when token missing."""
        token = extract_bearer_token("Bearer")
        assert token is None


class TestAPIKeyAuth:
    """Tests for APIKeyAuth class."""

    def test_init_with_keys(self):
        """Initialize with explicit keys."""
        auth = APIKeyAuth(api_keys=["key1", "key2"])
        assert len(auth._key_hashes) == 2

    def test_verify_valid_key(self):
        """Verify a valid API key."""
        key = "test_api_key_12345"
        auth = APIKeyAuth(api_keys=[key])
        assert auth.verify(key) is True

    def test_verify_invalid_key(self):
        """Reject an invalid API key."""
        auth = APIKeyAuth(api_keys=["valid_key"])
        assert auth.verify("invalid_key") is False

    def test_verify_empty_key(self):
        """Reject empty key."""
        auth = APIKeyAuth(api_keys=["valid_key"])
        assert auth.verify("") is False

    def test_no_keys_allows_all(self):
        """When no keys configured, allow all requests."""
        auth = APIKeyAuth(api_keys=[])
        assert auth.verify("any_key") is True

    def test_rate_limiting(self):
        """Rate limiting should block excess requests."""
        key = "test_key"
        auth = APIKeyAuth(api_keys=[key], rate_limit=5, rate_window=60)

        # First 5 requests should succeed
        for _ in range(5):
            assert auth.verify(key) is True

        # 6th request should be rate limited
        assert auth.verify(key) is False

    def test_failed_attempts_tracking(self):
        """Track failed authentication attempts."""
        auth = APIKeyAuth(api_keys=["valid_key"])
        client_ip = "192.168.1.100"

        # Make some failed attempts
        for _ in range(5):
            auth.verify("invalid_key", client_ip)

        # Check attempts are tracked
        assert client_ip in auth._failed_attempts
        assert len(auth._failed_attempts[client_ip]) == 5

    def test_ip_blocking(self):
        """Block IP after too many failed attempts."""
        auth = APIKeyAuth(api_keys=["valid_key"])
        client_ip = "192.168.1.100"

        # Make 20 failed attempts
        for _ in range(20):
            auth.verify("invalid_key", client_ip)

        # IP should now be blocked
        assert auth.is_blocked(client_ip) is True

    def test_ip_not_blocked_under_threshold(self):
        """IP should not be blocked under threshold."""
        auth = APIKeyAuth(api_keys=["valid_key"])
        client_ip = "192.168.1.100"

        # Make 10 failed attempts (under default 20)
        for _ in range(10):
            auth.verify("invalid_key", client_ip)

        assert auth.is_blocked(client_ip) is False

    def test_get_stats(self):
        """Get authentication statistics."""
        auth = APIKeyAuth(api_keys=["key1", "key2"])
        stats = auth.get_stats()

        assert stats["keys_configured"] == 2
        assert "total_requests_last_minute" in stats
        assert "blocked_ips" in stats
        assert "failed_attempts_last_hour" in stats


class TestGlobalAuthFunctions:
    """Tests for global authentication functions."""

    def test_verify_api_key_function(self, monkeypatch):
        """Test the global verify_api_key function."""
        # Set environment variable for test
        monkeypatch.setenv("MCP_API_KEY", "global_test_key")

        # Reset global instance
        import src.dolibarr_mcp.auth.api_key as auth_module
        auth_module._auth_instance = None

        # Should verify the key
        assert verify_api_key("global_test_key") is True
        assert verify_api_key("wrong_key") is False
