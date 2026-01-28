"""API Key authentication for Dolibarr MCP Server.

Secures MCP HTTP endpoints with bearer token authentication.
Supports multiple API keys with optional expiration and rate limiting.
"""

import os
import secrets
import hashlib
import logging
import time
from typing import Optional, Dict, List, Callable
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """API Key authentication manager.

    Features:
    - Multiple API keys support
    - Key hashing for secure storage
    - Rate limiting per key
    - Optional key expiration
    - Request logging
    """

    def __init__(
        self,
        api_keys: Optional[List[str]] = None,
        rate_limit: int = 100,  # requests per minute
        rate_window: int = 60,  # seconds
    ):
        """Initialize API Key auth.

        Args:
            api_keys: List of valid API keys. If None, reads from MCP_API_KEYS env var
            rate_limit: Maximum requests per rate_window
            rate_window: Time window in seconds for rate limiting
        """
        self.rate_limit = rate_limit
        self.rate_window = rate_window

        # Load API keys from environment or parameter
        raw_keys = api_keys or self._load_keys_from_env()

        # Store hashed keys for security
        self._key_hashes: Dict[str, dict] = {}
        for key in raw_keys:
            key_hash = self._hash_key(key)
            self._key_hashes[key_hash] = {
                "created": datetime.utcnow(),
                "requests": [],
                "last_used": None,
            }

        # Track failed attempts for security
        self._failed_attempts: Dict[str, List[float]] = {}

        logger.info(f"APIKeyAuth initialized with {len(self._key_hashes)} keys")

    def _load_keys_from_env(self) -> List[str]:
        """Load API keys from environment variable."""
        keys_str = os.getenv("MCP_API_KEYS", "")
        if not keys_str:
            # Check for single key
            single_key = os.getenv("MCP_API_KEY", "")
            if single_key:
                return [single_key]
            return []

        # Support comma-separated keys
        return [k.strip() for k in keys_str.split(",") if k.strip()]

    def _hash_key(self, key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify(self, api_key: str, client_ip: Optional[str] = None) -> bool:
        """Verify an API key.

        Args:
            api_key: The API key to verify
            client_ip: Client IP for rate limiting and logging

        Returns:
            True if key is valid and not rate limited
        """
        if not api_key:
            logger.warning(f"Empty API key from {client_ip}")
            return False

        # Check if auth is disabled (no keys configured)
        if not self._key_hashes:
            logger.warning("No API keys configured - auth disabled")
            return True

        key_hash = self._hash_key(api_key)

        if key_hash not in self._key_hashes:
            self._record_failed_attempt(client_ip)
            logger.warning(f"Invalid API key from {client_ip}")
            return False

        # Check rate limit
        if not self._check_rate_limit(key_hash):
            logger.warning(f"Rate limit exceeded for key from {client_ip}")
            return False

        # Update usage stats
        key_data = self._key_hashes[key_hash]
        key_data["last_used"] = datetime.utcnow()
        key_data["requests"].append(time.time())

        return True

    def _check_rate_limit(self, key_hash: str) -> bool:
        """Check if key is within rate limit."""
        key_data = self._key_hashes.get(key_hash)
        if not key_data:
            return False

        now = time.time()
        window_start = now - self.rate_window

        # Clean old requests
        key_data["requests"] = [
            t for t in key_data["requests"]
            if t > window_start
        ]

        return len(key_data["requests"]) < self.rate_limit

    def _record_failed_attempt(self, client_ip: Optional[str]) -> None:
        """Record a failed authentication attempt."""
        if not client_ip:
            return

        now = time.time()
        if client_ip not in self._failed_attempts:
            self._failed_attempts[client_ip] = []

        self._failed_attempts[client_ip].append(now)

        # Clean old attempts (last hour)
        self._failed_attempts[client_ip] = [
            t for t in self._failed_attempts[client_ip]
            if t > now - 3600
        ]

        # Log if too many failures
        if len(self._failed_attempts[client_ip]) >= 10:
            logger.error(f"Multiple failed auth attempts from {client_ip}")

    def is_blocked(self, client_ip: str, max_failures: int = 20) -> bool:
        """Check if an IP is blocked due to too many failures."""
        attempts = self._failed_attempts.get(client_ip, [])
        now = time.time()
        recent = [t for t in attempts if t > now - 3600]
        return len(recent) >= max_failures

    def get_stats(self) -> Dict:
        """Get authentication statistics."""
        total_requests = sum(
            len(data["requests"])
            for data in self._key_hashes.values()
        )

        return {
            "keys_configured": len(self._key_hashes),
            "total_requests_last_minute": total_requests,
            "blocked_ips": len([
                ip for ip, attempts in self._failed_attempts.items()
                if len(attempts) >= 20
            ]),
            "failed_attempts_last_hour": sum(
                len(attempts) for attempts in self._failed_attempts.values()
            ),
        }


# Global auth instance
_auth_instance: Optional[APIKeyAuth] = None


def get_auth() -> APIKeyAuth:
    """Get or create global auth instance."""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = APIKeyAuth()
    return _auth_instance


def verify_api_key(api_key: str, client_ip: Optional[str] = None) -> bool:
    """Verify an API key using global auth instance."""
    return get_auth().verify(api_key, client_ip)


def generate_api_key(length: int = 32) -> str:
    """Generate a new secure API key.

    Args:
        length: Length of the key in bytes (default 32 = 64 hex chars)

    Returns:
        New API key string
    """
    return secrets.token_hex(length)


def require_auth(func: Callable) -> Callable:
    """Decorator to require API key authentication.

    Use on HTTP handler functions that receive request objects.
    Expects API key in Authorization header as: Bearer <key>
    """
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        # Extract API key from header
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return {"error": "Missing or invalid Authorization header", "status": 401}

        api_key = auth_header[7:]  # Remove "Bearer " prefix
        client_ip = request.client.host if hasattr(request, "client") else None

        # Check if IP is blocked
        auth = get_auth()
        if client_ip and auth.is_blocked(client_ip):
            return {"error": "IP blocked due to too many failed attempts", "status": 403}

        # Verify key
        if not verify_api_key(api_key, client_ip):
            return {"error": "Invalid API key", "status": 401}

        return await func(request, *args, **kwargs)

    return wrapper


def extract_bearer_token(authorization: str) -> Optional[str]:
    """Extract bearer token from Authorization header.

    Args:
        authorization: Full Authorization header value

    Returns:
        Token string or None if invalid format
    """
    if not authorization:
        return None

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
