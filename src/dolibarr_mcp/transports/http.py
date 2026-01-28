"""HTTP transport for MCP server with API Key authentication.

This module handles communication over HTTP using Starlette/ASGI,
which enables web-based MCP clients like Open WebUI.

Security features:
- API Key authentication (Bearer token)
- Rate limiting per key
- IP blocking for failed attempts
- Request logging
"""

import os
import sys
import logging
from typing import Any, Optional

from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route
from starlette.types import Receive, Scope, Send
import uvicorn

from ..auth.api_key import APIKeyAuth, extract_bearer_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API Key authentication."""

    def __init__(self, app: Any, auth: APIKeyAuth, auth_enabled: bool = True):
        super().__init__(app)
        self.auth = auth
        self.auth_enabled = auth_enabled

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health checks and OPTIONS
        if request.url.path in ["/health", "/healthz", "/ready"]:
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip auth if disabled
        if not self.auth_enabled:
            return await call_next(request)

        # Extract client IP
        client_ip = request.client.host if request.client else None

        # Check if IP is blocked
        if client_ip and self.auth.is_blocked(client_ip):
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                {"error": "Access denied", "code": "IP_BLOCKED"},
                status_code=403
            )

        # Extract and verify API key
        auth_header = request.headers.get("Authorization", "")
        api_key = extract_bearer_token(auth_header)

        if not api_key:
            return JSONResponse(
                {
                    "error": "Missing API key",
                    "code": "AUTH_REQUIRED",
                    "hint": "Include 'Authorization: Bearer <your-api-key>' header"
                },
                status_code=401
            )

        if not self.auth.verify(api_key, client_ip):
            return JSONResponse(
                {"error": "Invalid API key", "code": "AUTH_FAILED"},
                status_code=401
            )

        # Add auth info to request state
        request.state.authenticated = True
        request.state.client_ip = client_ip

        return await call_next(request)


class ASGIEndpoint:
    """ASGI endpoint wrapper for StreamableHTTP handler."""

    def __init__(self, handler: Any):
        self.handler = handler

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.handler(scope, receive, send)


def build_http_app(
    session_manager: StreamableHTTPSessionManager,
    auth: Optional[APIKeyAuth] = None,
    auth_enabled: bool = True
) -> Starlette:
    """Create HTTP app for StreamableHTTP transport with authentication.

    Args:
        session_manager: MCP session manager instance
        auth: APIKeyAuth instance (creates default if None)
        auth_enabled: Whether to enable authentication

    Returns:
        Starlette ASGI application
    """
    if auth is None:
        auth = APIKeyAuth()

    async def options_handler(request: Request) -> Response:
        """Handle CORS preflight requests."""
        return Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
            },
        )

    async def health_handler(request: Request) -> JSONResponse:
        """Health check endpoint (no auth required)."""
        return JSONResponse({
            "status": "healthy",
            "service": "dolibarr-mcp",
            "version": "2.1.0",
            "auth_enabled": auth_enabled,
        })

    async def stats_handler(request: Request) -> JSONResponse:
        """Auth stats endpoint (requires auth)."""
        return JSONResponse(auth.get_stats())

    async def lifespan(app: Any) -> Any:
        """Application lifespan handler."""
        async with session_manager.run():
            yield

    async def asgi_handler(scope: Scope, receive: Receive, send: Send) -> None:
        """Main ASGI request handler."""
        await session_manager.handle_request(scope, receive, send)

    app = Starlette(
        routes=[
            # Health check (no auth)
            Route("/health", health_handler, methods=["GET"]),
            Route("/healthz", health_handler, methods=["GET"]),
            Route("/ready", health_handler, methods=["GET"]),

            # Stats (requires auth)
            Route("/stats", stats_handler, methods=["GET"]),

            # MCP endpoints
            Route("/", ASGIEndpoint(asgi_handler), methods=["GET", "POST", "DELETE"]),
            Route("/{path:path}", ASGIEndpoint(asgi_handler), methods=["GET", "POST", "DELETE"]),

            # CORS preflight
            Route("/", options_handler, methods=["OPTIONS"]),
            Route("/{path:path}", options_handler, methods=["OPTIONS"]),
        ],
        lifespan=lifespan,
    )

    # Add authentication middleware
    app.add_middleware(AuthMiddleware, auth=auth, auth_enabled=auth_enabled)

    # Add CORS middleware for cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        allow_credentials=False,
    )

    return app


async def run_http_server(
    server: Server,
    host: str = "0.0.0.0",
    port: int = 8080,
    log_level: str = "warning",
    auth_enabled: Optional[bool] = None,
) -> None:
    """Run MCP server over HTTP transport with authentication.

    This enables web-based MCP clients like Open WebUI to connect
    to the Dolibarr MCP server securely.

    Args:
        server: The MCP Server instance
        host: HTTP host/interface to bind
        port: HTTP port to listen on
        log_level: Logging level (debug, info, warning, error)
        auth_enabled: Enable API key auth (default: from MCP_AUTH_ENABLED env)
    """
    # Determine if auth should be enabled
    if auth_enabled is None:
        auth_enabled = os.getenv("MCP_AUTH_ENABLED", "true").lower() == "true"

    # Create auth instance
    auth = APIKeyAuth()

    # Warn if no keys configured
    if auth_enabled and not auth._key_hashes:
        logger.warning("⚠️  Auth enabled but no API keys configured!")
        logger.warning("   Set MCP_API_KEY or MCP_API_KEYS environment variable")
        logger.warning("   Or disable auth with MCP_AUTH_ENABLED=false")

    session_manager = StreamableHTTPSessionManager(
        server,
        json_response=False,
        stateless=False
    )

    app = build_http_app(session_manager, auth=auth, auth_enabled=auth_enabled)

    auth_status = "🔐 Auth enabled" if auth_enabled else "⚠️  Auth disabled"
    print(f"🌐 HTTP server on {host}:{port} | {auth_status}", file=sys.stderr)

    uvicorn_config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=log_level.lower(),
        loop="asyncio",
        access_log=False,
    )

    await uvicorn.Server(uvicorn_config).serve()
