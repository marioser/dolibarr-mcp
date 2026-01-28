"""Optimized Dolibarr MCP Server - Token-efficient implementation.

Features:
- TOON format output for ~60% token reduction
- DragonflyDB/Redis cache with automatic invalidation
- Field filtering for minimal response size
"""

import asyncio
import json
import sys
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import Tool, TextContent

from .config import Config
from .dolibarr_client import DolibarrClient, DolibarrAPIError

# TOON format and Cache imports
from .formats.toon_encoder import ToonEncoder
from .cache.dragonfly import DragonflyCache
from .cache.strategies import should_cache, get_ttl_for_entity, get_invalidation_targets

# Global cache instance
_cache: Optional[DragonflyCache] = None
_toon_encoder = ToonEncoder()

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response
from starlette.routing import Route
from starlette.types import Receive, Scope, Send
import uvicorn

# Authentication imports
from .auth.api_key import APIKeyAuth

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

server = Server("dolibarr-mcp")

# =============================================================================
# RESPONSE FILTERS - Reduce token usage by returning only essential fields
# =============================================================================

CUSTOMER_FIELDS = ["id", "name", "name_alias", "email", "phone", "address", "town", "zip",
                   "country_code", "client", "fournisseur", "code_client", "status"]

PRODUCT_FIELDS = ["id", "ref", "label", "description", "price", "price_ttc", "type",
                  "status", "stock_reel", "barcode"]

INVOICE_FIELDS = ["id", "ref", "socid", "date", "date_lim_reglement", "total_ht", "total_tva",
                  "total_ttc", "paye", "status", "lines"]

ORDER_FIELDS = ["id", "ref", "socid", "date", "total_ht", "total_ttc", "status", "lines"]

PROPOSAL_FIELDS = ["id", "ref", "socid", "date", "fin_validite", "total_ht", "total_tva",
                   "total_ttc", "status", "lines"]

PROJECT_FIELDS = ["id", "ref", "title", "description", "socid", "status", "date_start", "date_end"]

CONTACT_FIELDS = ["id", "firstname", "lastname", "email", "phone", "socid"]

USER_FIELDS = ["id", "login", "lastname", "firstname", "email", "admin", "status"]

LINE_FIELDS = ["id", "fk_product", "desc", "qty", "subprice", "total_ht", "total_ttc", "tva_tx"]


def _filter_fields(data: Any, fields: List[str]) -> Any:
    """Filter response to include only specified fields."""
    if isinstance(data, list):
        return [_filter_fields(item, fields) for item in data]
    if isinstance(data, dict):
        result = {k: v for k, v in data.items() if k in fields}
        # Handle nested lines
        if "lines" in data and "lines" in fields:
            result["lines"] = [_filter_fields(line, LINE_FIELDS) for line in data.get("lines", [])]
        return result
    return data


def _escape_sqlfilter(value: str) -> str:
    """Escape single quotes for SQL filters."""
    return value.replace("'", "''")


# =============================================================================
# TOOL SCHEMA HELPERS - Reduce code duplication
# =============================================================================

def _id_schema(name: str) -> dict:
    """Generate simple ID-based schema."""
    return {
        "type": "object",
        "properties": {name: {"type": "integer", "description": f"{name}"}},
        "required": [name],
        "additionalProperties": False
    }

def _list_schema(with_status: bool = False, status_type: str = "string") -> dict:
    """Generate list/pagination schema."""
    props = {"limit": {"type": "integer", "default": 100}}
    if with_status:
        props["status"] = {"type": status_type}
    return {"type": "object", "properties": props, "additionalProperties": False}

def _search_schema() -> dict:
    """Generate search schema."""
    return {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 20}
        },
        "required": ["query"],
        "additionalProperties": False
    }

def _line_schema(entity: str) -> dict:
    """Generate line item schema for invoices/proposals/orders."""
    return {
        "type": "object",
        "properties": {
            f"{entity}_id": {"type": "integer"},
            "desc": {"type": "string"},
            "qty": {"type": "number"},
            "subprice": {"type": "number"},
            "product_id": {"type": "integer"},
            "product_type": {"type": "integer", "default": 0},
            "tva_tx": {"type": "number"}
        },
        "required": [f"{entity}_id", "desc", "qty", "subprice"],
        "additionalProperties": False
    }


# =============================================================================
# TOOL DEFINITIONS - Concise descriptions for token efficiency
# =============================================================================

@server.list_tools()
async def handle_list_tools():
    """List all available tools."""
    return [
        # System
        Tool(name="test_connection", description="Test Dolibarr API connection",
             inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),
        Tool(name="get_status", description="Get Dolibarr system status",
             inputSchema={"type": "object", "properties": {}, "additionalProperties": False}),

        # Search (consolidated)
        Tool(name="search_products_by_ref", description="Search products by reference prefix",
             inputSchema={"type": "object", "properties": {"ref_prefix": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, "required": ["ref_prefix"], "additionalProperties": False}),
        Tool(name="search_products_by_label", description="Search products by label/name",
             inputSchema=_search_schema()),
        Tool(name="search_customers", description="Search customers by name/alias",
             inputSchema=_search_schema()),
        Tool(name="resolve_product_ref", description="Get exact product by reference",
             inputSchema={"type": "object", "properties": {"ref": {"type": "string"}}, "required": ["ref"], "additionalProperties": False}),

        # Users
        Tool(name="get_users", description="List users (paginated)",
             inputSchema={"type": "object", "properties": {"limit": {"type": "integer", "default": 100}, "page": {"type": "integer", "default": 1}}, "additionalProperties": False}),
        Tool(name="get_user_by_id", description="Get user by ID", inputSchema=_id_schema("user_id")),
        Tool(name="create_user", description="Create user",
             inputSchema={"type": "object", "properties": {"login": {"type": "string"}, "lastname": {"type": "string"}, "firstname": {"type": "string"}, "email": {"type": "string"}, "password": {"type": "string"}, "admin": {"type": "integer", "default": 0}}, "required": ["login", "lastname"], "additionalProperties": False}),
        Tool(name="update_user", description="Update user",
             inputSchema={"type": "object", "properties": {"user_id": {"type": "integer"}, "login": {"type": "string"}, "lastname": {"type": "string"}, "firstname": {"type": "string"}, "email": {"type": "string"}, "admin": {"type": "integer"}}, "required": ["user_id"], "additionalProperties": False}),
        Tool(name="delete_user", description="Delete user", inputSchema=_id_schema("user_id")),

        # Customers
        Tool(name="get_customers", description="List customers (paginated)",
             inputSchema={"type": "object", "properties": {"limit": {"type": "integer", "default": 100}, "page": {"type": "integer", "default": 1}}, "additionalProperties": False}),
        Tool(name="get_customer_by_id", description="Get customer by ID", inputSchema=_id_schema("customer_id")),
        Tool(name="create_customer", description="Create customer",
             inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "address": {"type": "string"}, "town": {"type": "string"}, "zip": {"type": "string"}, "country_id": {"type": "integer", "default": 1}, "type": {"type": "integer", "default": 1}, "status": {"type": "integer", "default": 1}}, "required": ["name"], "additionalProperties": False}),
        Tool(name="update_customer", description="Update customer",
             inputSchema={"type": "object", "properties": {"customer_id": {"type": "integer"}, "name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "address": {"type": "string"}, "town": {"type": "string"}, "zip": {"type": "string"}, "status": {"type": "integer"}}, "required": ["customer_id"], "additionalProperties": False}),
        Tool(name="delete_customer", description="Delete customer", inputSchema=_id_schema("customer_id")),

        # Products
        Tool(name="get_products", description="List products", inputSchema=_list_schema()),
        Tool(name="get_product_by_id", description="Get product by ID", inputSchema=_id_schema("product_id")),
        Tool(name="create_product", description="Create product",
             inputSchema={"type": "object", "properties": {"label": {"type": "string"}, "price": {"type": "number"}, "description": {"type": "string"}, "stock": {"type": "integer"}}, "required": ["label", "price"], "additionalProperties": False}),
        Tool(name="update_product", description="Update product",
             inputSchema={"type": "object", "properties": {"product_id": {"type": "integer"}, "label": {"type": "string"}, "price": {"type": "number"}, "description": {"type": "string"}}, "required": ["product_id"], "additionalProperties": False}),
        Tool(name="delete_product", description="Delete product", inputSchema=_id_schema("product_id")),

        # Invoices
        Tool(name="get_invoices", description="List invoices. Status: draft, unpaid, paid", inputSchema=_list_schema(with_status=True)),
        Tool(name="get_invoice_by_id", description="Get invoice by ID", inputSchema=_id_schema("invoice_id")),
        Tool(name="create_invoice", description="Create invoice with lines",
             inputSchema={"type": "object", "properties": {
                 "customer_id": {"type": "integer"},
                 "date": {"type": "string"},
                 "due_date": {"type": "string"},
                 "lines": {"type": "array", "items": {"type": "object", "properties": {"desc": {"type": "string"}, "qty": {"type": "number"}, "subprice": {"type": "number"}, "product_id": {"type": "integer"}, "product_type": {"type": "integer"}, "vat": {"type": "number"}}, "required": ["desc", "qty", "subprice"]}}
             }, "required": ["customer_id", "lines"], "additionalProperties": False}),
        Tool(name="update_invoice", description="Update invoice",
             inputSchema={"type": "object", "properties": {"invoice_id": {"type": "integer"}, "date": {"type": "string"}, "due_date": {"type": "string"}}, "required": ["invoice_id"], "additionalProperties": False}),
        Tool(name="delete_invoice", description="Delete invoice", inputSchema=_id_schema("invoice_id")),
        Tool(name="add_invoice_line", description="Add line to invoice", inputSchema=_line_schema("invoice")),
        Tool(name="update_invoice_line", description="Update invoice line",
             inputSchema={"type": "object", "properties": {"invoice_id": {"type": "integer"}, "line_id": {"type": "integer"}, "desc": {"type": "string"}, "qty": {"type": "number"}, "subprice": {"type": "number"}, "vat": {"type": "number"}}, "required": ["invoice_id", "line_id"], "additionalProperties": False}),
        Tool(name="delete_invoice_line", description="Delete invoice line",
             inputSchema={"type": "object", "properties": {"invoice_id": {"type": "integer"}, "line_id": {"type": "integer"}}, "required": ["invoice_id", "line_id"], "additionalProperties": False}),
        Tool(name="validate_invoice", description="Validate draft invoice",
             inputSchema={"type": "object", "properties": {"invoice_id": {"type": "integer"}, "warehouse_id": {"type": "integer", "default": 0}}, "required": ["invoice_id"], "additionalProperties": False}),

        # Orders
        Tool(name="get_orders", description="List orders", inputSchema=_list_schema(with_status=True)),
        Tool(name="get_order_by_id", description="Get order by ID", inputSchema=_id_schema("order_id")),
        Tool(name="create_order", description="Create order",
             inputSchema={"type": "object", "properties": {"customer_id": {"type": "integer"}, "date": {"type": "string"}}, "required": ["customer_id"], "additionalProperties": False}),
        Tool(name="update_order", description="Update order",
             inputSchema={"type": "object", "properties": {"order_id": {"type": "integer"}, "date": {"type": "string"}}, "required": ["order_id"], "additionalProperties": False}),
        Tool(name="delete_order", description="Delete order", inputSchema=_id_schema("order_id")),

        # Contacts
        Tool(name="get_contacts", description="List contacts", inputSchema=_list_schema()),
        Tool(name="get_contact_by_id", description="Get contact by ID", inputSchema=_id_schema("contact_id")),
        Tool(name="create_contact", description="Create contact",
             inputSchema={"type": "object", "properties": {"firstname": {"type": "string"}, "lastname": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}, "socid": {"type": "integer"}}, "required": ["firstname", "lastname"], "additionalProperties": False}),
        Tool(name="update_contact", description="Update contact",
             inputSchema={"type": "object", "properties": {"contact_id": {"type": "integer"}, "firstname": {"type": "string"}, "lastname": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}}, "required": ["contact_id"], "additionalProperties": False}),
        Tool(name="delete_contact", description="Delete contact", inputSchema=_id_schema("contact_id")),

        # Projects
        Tool(name="get_projects", description="List projects. Status: 0=draft, 1=open, 2=closed",
             inputSchema={"type": "object", "properties": {"limit": {"type": "integer", "default": 100}, "page": {"type": "integer", "default": 1}, "status": {"type": "integer", "default": 1}}, "additionalProperties": False}),
        Tool(name="get_project_by_id", description="Get project by ID", inputSchema=_id_schema("project_id")),
        Tool(name="search_projects", description="Search projects by ref/title", inputSchema=_search_schema()),
        Tool(name="create_project", description="Create project",
             inputSchema={"type": "object", "properties": {"title": {"type": "string"}, "ref": {"type": "string"}, "description": {"type": "string"}, "socid": {"type": "integer"}, "status": {"type": "integer", "default": 1}}, "required": ["title"], "additionalProperties": False}),
        Tool(name="update_project", description="Update project",
             inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "status": {"type": "integer"}}, "required": ["project_id"], "additionalProperties": False}),
        Tool(name="delete_project", description="Delete project", inputSchema=_id_schema("project_id")),

        # Proposals
        Tool(name="get_proposals", description="List proposals. Status: 0=draft, 1=validated, 2=signed, 3=refused",
             inputSchema=_list_schema(with_status=True, status_type="integer")),
        Tool(name="get_proposal_by_id", description="Get proposal by ID", inputSchema=_id_schema("proposal_id")),
        Tool(name="search_proposals", description="Search proposals by ref/customer", inputSchema=_search_schema()),
        Tool(name="create_proposal", description="Create proposal with optional lines",
             inputSchema={"type": "object", "properties": {
                 "customer_id": {"type": "integer"},
                 "date": {"type": "string"},
                 "duree_validite": {"type": "integer", "default": 30},
                 "project_id": {"type": "integer"},
                 "note_public": {"type": "string"},
                 "note_private": {"type": "string"},
                 "lines": {"type": "array", "items": {"type": "object", "properties": {"desc": {"type": "string"}, "qty": {"type": "number"}, "subprice": {"type": "number"}, "product_id": {"type": "integer"}, "product_type": {"type": "integer"}, "tva_tx": {"type": "number"}, "remise_percent": {"type": "number"}}, "required": ["desc", "qty", "subprice"]}}
             }, "required": ["customer_id"], "additionalProperties": False}),
        Tool(name="update_proposal", description="Update draft proposal",
             inputSchema={"type": "object", "properties": {"proposal_id": {"type": "integer"}, "duree_validite": {"type": "integer"}, "note_public": {"type": "string"}, "note_private": {"type": "string"}}, "required": ["proposal_id"], "additionalProperties": False}),
        Tool(name="delete_proposal", description="Delete proposal", inputSchema=_id_schema("proposal_id")),
        Tool(name="add_proposal_line", description="Add line to proposal", inputSchema=_line_schema("proposal")),
        Tool(name="update_proposal_line", description="Update proposal line",
             inputSchema={"type": "object", "properties": {"proposal_id": {"type": "integer"}, "line_id": {"type": "integer"}, "desc": {"type": "string"}, "qty": {"type": "number"}, "subprice": {"type": "number"}, "tva_tx": {"type": "number"}}, "required": ["proposal_id", "line_id"], "additionalProperties": False}),
        Tool(name="delete_proposal_line", description="Delete proposal line",
             inputSchema={"type": "object", "properties": {"proposal_id": {"type": "integer"}, "line_id": {"type": "integer"}}, "required": ["proposal_id", "line_id"], "additionalProperties": False}),
        Tool(name="validate_proposal", description="Validate draft proposal", inputSchema=_id_schema("proposal_id")),
        Tool(name="close_proposal", description="Close proposal: status 2=signed/won, 3=refused/lost",
             inputSchema={"type": "object", "properties": {"proposal_id": {"type": "integer"}, "status": {"type": "integer", "enum": [2, 3]}, "note": {"type": "string"}}, "required": ["proposal_id", "status"], "additionalProperties": False}),
        Tool(name="set_proposal_to_draft", description="Revert proposal to draft", inputSchema=_id_schema("proposal_id")),

        # Raw API (escape hatch)
        Tool(name="dolibarr_raw_api", description="Direct API call (use only if no specific tool exists)",
             inputSchema={"type": "object", "properties": {"method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]}, "endpoint": {"type": "string"}, "params": {"type": "object"}, "data": {"type": "object"}}, "required": ["method", "endpoint"], "additionalProperties": False}),
    ]


# =============================================================================
# TOOL HANDLERS - Optimized with response filtering
# =============================================================================

async def _get_cache() -> Optional[DragonflyCache]:
    """Get or initialize cache instance."""
    global _cache
    if _cache is None:
        cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        if cache_enabled:
            _cache = DragonflyCache(
                host=os.getenv("DRAGONFLY_HOST", "localhost"),
                port=int(os.getenv("DRAGONFLY_PORT", "6379")),
                password=os.getenv("DRAGONFLY_PASSWORD"),
                prefix="dolibarr:",
                enabled=True
            )
            await _cache.connect()
    return _cache


def _format_response(data: Any, use_toon: bool = True) -> str:
    """Format response as TOON or JSON."""
    if use_toon:
        try:
            return _toon_encoder.encode(data)
        except Exception:
            pass  # Fallback to JSON
    return json.dumps(data, indent=2, default=str)


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle tool calls with caching and TOON format responses."""
    global _cache
    use_toon = os.getenv("OUTPUT_FORMAT", "toon").lower() == "toon"

    try:
        # Initialize cache if needed
        cache = await _get_cache()

        # Check cache for read operations
        cache_key = None
        if cache and cache._connected and should_cache(name):
            cache_key = cache.make_tool_key(name, arguments)
            cached = await cache.get(cache_key)
            if cached is not None:
                logging.debug(f"Cache HIT: {name}")
                return [TextContent(type="text", text=_format_response(cached, use_toon))]

        # Execute tool
        config = Config()
        async with DolibarrClient(config) as client:
            result = await _dispatch_tool(client, name, arguments)

        # Cache result for read operations
        if cache and cache._connected and cache_key and should_cache(name):
            ttl = get_ttl_for_entity(name)
            await cache.set(cache_key, result, ttl)
            logging.debug(f"Cache SET: {name} (TTL: {ttl}s)")

        # Invalidate related caches for write operations
        if cache and cache._connected:
            targets = get_invalidation_targets(name)
            for target in targets:
                await cache.invalidate_pattern(f"tool:{target}:*")

        return [TextContent(type="text", text=_format_response(result, use_toon))]

    except DolibarrAPIError as e:
        error_response = {"error": str(e), "status": e.status_code or 500}
        return [TextContent(type="text", text=_format_response(error_response, use_toon))]
    except Exception as e:
        error_response = {"error": f"Tool failed: {e}", "status": 500}
        return [TextContent(type="text", text=_format_response(error_response, use_toon))]


async def _dispatch_tool(client: DolibarrClient, name: str, args: dict) -> Any:
    """Dispatch tool call to appropriate handler with response filtering."""

    # System
    if name == "test_connection":
        return await client.get_status()
    if name == "get_status":
        return await client.get_status()

    # Search
    if name == "search_products_by_ref":
        ref = _escape_sqlfilter(args["ref_prefix"])
        result = await client.search_products(f"(t.ref:like:'{ref}%')", args.get("limit", 20))
        return _filter_fields(result, PRODUCT_FIELDS)
    if name == "search_products_by_label":
        label = _escape_sqlfilter(args["query"])
        result = await client.search_products(f"(t.label:like:'%{label}%')", args.get("limit", 20))
        return _filter_fields(result, PRODUCT_FIELDS)
    if name == "search_customers":
        q = _escape_sqlfilter(args["query"])
        result = await client.search_customers(f"((t.nom:like:'%{q}%') OR (t.name_alias:like:'%{q}%'))", args.get("limit", 20))
        return _filter_fields(result, CUSTOMER_FIELDS)
    if name == "resolve_product_ref":
        ref = args["ref"]
        products = await client.search_products(f"(t.ref:like:'{_escape_sqlfilter(ref)}')", 2)
        if not products:
            return {"status": "not_found", "ref": ref}
        if len(products) == 1:
            return {"status": "ok", "product": _filter_fields(products[0], PRODUCT_FIELDS)}
        exact = [p for p in products if p.get("ref") == ref]
        if len(exact) == 1:
            return {"status": "ok", "product": _filter_fields(exact[0], PRODUCT_FIELDS)}
        return {"status": "ambiguous", "products": _filter_fields(products, PRODUCT_FIELDS)}

    # Users
    if name == "get_users":
        result = await client.get_users(args.get("limit", 100), args.get("page", 1))
        return _filter_fields(result, USER_FIELDS)
    if name == "get_user_by_id":
        result = await client.get_user_by_id(args["user_id"])
        return _filter_fields(result, USER_FIELDS)
    if name == "create_user":
        return await client.create_user(**args)
    if name == "update_user":
        uid = args.pop("user_id")
        return await client.update_user(uid, **args)
    if name == "delete_user":
        return await client.delete_user(args["user_id"])

    # Customers
    if name == "get_customers":
        result = await client.get_customers(args.get("limit", 100), args.get("page", 1))
        return _filter_fields(result, CUSTOMER_FIELDS)
    if name == "get_customer_by_id":
        result = await client.get_customer_by_id(args["customer_id"])
        return _filter_fields(result, CUSTOMER_FIELDS)
    if name == "create_customer":
        return await client.create_customer(**args)
    if name == "update_customer":
        cid = args.pop("customer_id")
        return await client.update_customer(cid, **args)
    if name == "delete_customer":
        return await client.delete_customer(args["customer_id"])

    # Products
    if name == "get_products":
        result = await client.get_products(args.get("limit", 100))
        return _filter_fields(result, PRODUCT_FIELDS)
    if name == "get_product_by_id":
        result = await client.get_product_by_id(args["product_id"])
        return _filter_fields(result, PRODUCT_FIELDS)
    if name == "create_product":
        return await client.create_product(**args)
    if name == "update_product":
        pid = args.pop("product_id")
        return await client.update_product(pid, **args)
    if name == "delete_product":
        return await client.delete_product(args["product_id"])

    # Invoices
    if name == "get_invoices":
        result = await client.get_invoices(args.get("limit", 100), args.get("status"))
        return _filter_fields(result, INVOICE_FIELDS)
    if name == "get_invoice_by_id":
        result = await client.get_invoice_by_id(args["invoice_id"])
        return _filter_fields(result, INVOICE_FIELDS)
    if name == "create_invoice":
        return await client.create_invoice(**args)
    if name == "update_invoice":
        iid = args.pop("invoice_id")
        return await client.update_invoice(iid, **args)
    if name == "delete_invoice":
        return await client.delete_invoice(args["invoice_id"])
    if name == "add_invoice_line":
        iid = args.pop("invoice_id")
        return await client.add_invoice_line(iid, **args)
    if name == "update_invoice_line":
        iid, lid = args.pop("invoice_id"), args.pop("line_id")
        return await client.update_invoice_line(iid, lid, **args)
    if name == "delete_invoice_line":
        return await client.delete_invoice_line(args["invoice_id"], args["line_id"])
    if name == "validate_invoice":
        return await client.validate_invoice(args["invoice_id"], args.get("warehouse_id", 0))

    # Orders
    if name == "get_orders":
        result = await client.get_orders(args.get("limit", 100), args.get("status"))
        return _filter_fields(result, ORDER_FIELDS)
    if name == "get_order_by_id":
        result = await client.get_order_by_id(args["order_id"])
        return _filter_fields(result, ORDER_FIELDS)
    if name == "create_order":
        return await client.create_order(**args)
    if name == "update_order":
        oid = args.pop("order_id")
        return await client.update_order(oid, **args)
    if name == "delete_order":
        return await client.delete_order(args["order_id"])

    # Contacts
    if name == "get_contacts":
        result = await client.get_contacts(args.get("limit", 100))
        return _filter_fields(result, CONTACT_FIELDS)
    if name == "get_contact_by_id":
        result = await client.get_contact_by_id(args["contact_id"])
        return _filter_fields(result, CONTACT_FIELDS)
    if name == "create_contact":
        return await client.create_contact(**args)
    if name == "update_contact":
        cid = args.pop("contact_id")
        return await client.update_contact(cid, **args)
    if name == "delete_contact":
        return await client.delete_contact(args["contact_id"])

    # Projects
    if name == "get_projects":
        result = await client.get_projects(args.get("limit", 100), args.get("page", 1), args.get("status"))
        return _filter_fields(result, PROJECT_FIELDS)
    if name == "get_project_by_id":
        result = await client.get_project_by_id(args["project_id"])
        return _filter_fields(result, PROJECT_FIELDS)
    if name == "search_projects":
        q = _escape_sqlfilter(args["query"])
        result = await client.search_projects(f"((t.ref:like:'%{q}%') OR (t.title:like:'%{q}%'))", args.get("limit", 20))
        return _filter_fields(result, PROJECT_FIELDS)
    if name == "create_project":
        return await client.create_project(**args)
    if name == "update_project":
        pid = args.pop("project_id")
        return await client.update_project(pid, **args)
    if name == "delete_project":
        return await client.delete_project(args["project_id"])

    # Proposals
    if name == "get_proposals":
        result = await client.get_proposals(args.get("limit", 100), args.get("status"))
        return _filter_fields(result, PROPOSAL_FIELDS)
    if name == "get_proposal_by_id":
        result = await client.get_proposal_by_id(args["proposal_id"])
        return _filter_fields(result, PROPOSAL_FIELDS)
    if name == "search_proposals":
        q = _escape_sqlfilter(args["query"])
        result = await client.search_proposals(f"((t.ref:like:'%{q}%') OR (s.nom:like:'%{q}%'))", args.get("limit", 20))
        return _filter_fields(result, PROPOSAL_FIELDS)
    if name == "create_proposal":
        return await client.create_proposal(**args)
    if name == "update_proposal":
        pid = args.pop("proposal_id")
        return await client.update_proposal(pid, **args)
    if name == "delete_proposal":
        return await client.delete_proposal(args["proposal_id"])
    if name == "add_proposal_line":
        pid = args.pop("proposal_id")
        return await client.add_proposal_line(pid, **args)
    if name == "update_proposal_line":
        pid, lid = args.pop("proposal_id"), args.pop("line_id")
        return await client.update_proposal_line(pid, lid, **args)
    if name == "delete_proposal_line":
        return await client.delete_proposal_line(args["proposal_id"], args["line_id"])
    if name == "validate_proposal":
        return await client.validate_proposal(args["proposal_id"])
    if name == "close_proposal":
        pid = args.pop("proposal_id")
        return await client.close_proposal(pid, args["status"], args.get("note", ""))
    if name == "set_proposal_to_draft":
        return await client.set_proposal_to_draft(args["proposal_id"])

    # Raw API
    if name == "dolibarr_raw_api":
        return await client.dolibarr_raw_api(**args)

    return {"error": f"Unknown tool: {name}"}


# =============================================================================
# SERVER STARTUP
# =============================================================================

@asynccontextmanager
async def test_api_connection(config: Config | None = None):
    """Test API connection."""
    try:
        if config is None:
            config = Config()
        if not config.dolibarr_url or "your-dolibarr" in config.dolibarr_url:
            print("⚠️ DOLIBARR_URL not configured", file=sys.stderr)
            yield False
            return
        if not config.api_key or "your_" in config.api_key:
            print("⚠️ DOLIBARR_API_KEY not configured", file=sys.stderr)
            yield False
            return
        async with DolibarrClient(config) as client:
            await client.get_status()
            print("✅ Dolibarr API connected", file=sys.stderr)
            yield True
    except Exception as e:
        print(f"⚠️ API test failed: {e}", file=sys.stderr)
        yield False


async def _run_stdio_server(_config: Config) -> None:
    """Run MCP server over STDIO."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="dolibarr-mcp",
                server_version="1.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def _build_http_app(session_manager: StreamableHTTPSessionManager, auth: Optional[APIKeyAuth] = None, auth_enabled: bool = True) -> Starlette:
    """Create HTTP app for StreamableHTTP transport with authentication."""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse
    from .auth.api_key import extract_bearer_token

    class AuthMiddleware(BaseHTTPMiddleware):
        """Middleware for API Key authentication."""

        async def dispatch(self, request, call_next):
            # Skip auth for health checks and OPTIONS
            if request.url.path in ["/health", "/healthz", "/ready"]:
                return await call_next(request)
            if request.method == "OPTIONS":
                return await call_next(request)
            # Skip auth if disabled
            if not auth_enabled:
                return await call_next(request)
            # Extract client IP
            client_ip = request.client.host if request.client else None
            # Check if IP is blocked
            if auth and client_ip and auth.is_blocked(client_ip):
                return JSONResponse({"error": "Access denied", "code": "IP_BLOCKED"}, status_code=403)
            # Extract and verify API key
            auth_header = request.headers.get("Authorization", "")
            api_key = extract_bearer_token(auth_header)
            if not api_key:
                return JSONResponse({
                    "error": "Missing API key",
                    "code": "AUTH_REQUIRED",
                    "hint": "Include 'Authorization: Bearer <your-api-key>' header"
                }, status_code=401)
            if auth and not auth.verify(api_key, client_ip):
                return JSONResponse({"error": "Invalid API key", "code": "AUTH_FAILED"}, status_code=401)
            return await call_next(request)

    class ASGIEndpoint:
        def __init__(self, handler):
            self.handler = handler
        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            await self.handler(scope, receive, send)

    async def options_handler(request):
        return Response(status_code=204, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
        })

    async def health_handler(request):
        """Health check endpoint (no auth required)."""
        return JSONResponse({
            "status": "healthy",
            "service": "dolibarr-mcp",
            "version": "2.1.0",
            "auth_enabled": auth_enabled,
        })

    async def lifespan(app):
        async with session_manager.run():
            yield

    async def asgi_handler(scope, receive, send):
        await session_manager.handle_request(scope, receive, send)

    app = Starlette(
        routes=[
            # Health check endpoints (no auth)
            Route("/health", health_handler, methods=["GET"]),
            Route("/healthz", health_handler, methods=["GET"]),
            Route("/ready", health_handler, methods=["GET"]),
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
    if auth_enabled and auth:
        app.add_middleware(AuthMiddleware)
    # Add CORS middleware
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["Authorization", "Content-Type", "Accept"], allow_credentials=False)
    return app


async def _run_http_server(config: Config) -> None:
    """Run MCP server over HTTP with authentication."""
    # Determine if auth should be enabled
    auth_enabled = os.getenv("MCP_AUTH_ENABLED", "true").lower() == "true"

    # Create auth instance
    auth = APIKeyAuth() if auth_enabled else None

    # Warn if no keys configured
    if auth_enabled and auth and not auth._key_hashes:
        print("⚠️  Auth enabled but no API keys configured!", file=sys.stderr)
        print("   Set MCP_API_KEY or MCP_API_KEYS environment variable", file=sys.stderr)
        print("   Or disable auth with MCP_AUTH_ENABLED=false", file=sys.stderr)

    session_manager = StreamableHTTPSessionManager(server, json_response=False, stateless=False)
    app = _build_http_app(session_manager, auth=auth, auth_enabled=auth_enabled)

    auth_status = "🔐 Auth enabled" if auth_enabled else "⚠️  Auth disabled"
    print(f"🌐 HTTP server on {config.mcp_http_host}:{config.mcp_http_port} | {auth_status}", file=sys.stderr)

    uvicorn_config = uvicorn.Config(app, host=config.mcp_http_host, port=config.mcp_http_port, log_level=config.log_level.lower(), loop="asyncio", access_log=False)
    await uvicorn.Server(uvicorn_config).serve()


async def main():
    """Run the Dolibarr MCP server."""
    config = Config()
    async with test_api_connection(config) as ok:
        if not ok:
            print("⚠️ Starting without valid API", file=sys.stderr)
    print("🚀 Dolibarr MCP server ready", file=sys.stderr)
    if config.mcp_transport == "http":
        await _run_http_server(config)
    else:
        await _run_stdio_server(config)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
