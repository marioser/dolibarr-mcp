"""Base schema helpers for Dolibarr MCP tools.

These helpers reduce code duplication when defining tool input schemas.
"""

from typing import Any, Dict, List, Optional


def id_schema(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Generate a simple ID-based schema for single-entity operations.

    Args:
        name: The parameter name (e.g., "user_id", "customer_id")
        description: Optional description (defaults to the parameter name)

    Returns:
        JSON Schema for a single required ID parameter

    Example:
        >>> id_schema("user_id")
        {
            "type": "object",
            "properties": {"user_id": {"type": "integer", "description": "user_id"}},
            "required": ["user_id"],
            "additionalProperties": False
        }
    """
    return {
        "type": "object",
        "properties": {
            name: {
                "type": "integer",
                "description": description or name
            }
        },
        "required": [name],
        "additionalProperties": False
    }


def list_schema(
    with_status: bool = False,
    status_type: str = "string",
    with_page: bool = False,
    default_limit: int = 100
) -> Dict[str, Any]:
    """Generate a schema for list/pagination operations.

    Args:
        with_status: Include a status filter parameter
        status_type: Type of status parameter ("string" or "integer")
        with_page: Include page parameter for pagination
        default_limit: Default limit value

    Returns:
        JSON Schema for list operation parameters

    Example:
        >>> list_schema(with_status=True, status_type="integer")
        {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 100, "description": "Max results (1-500)"},
                "status": {"type": "integer", "description": "Filter by status"}
            },
            "additionalProperties": False
        }
    """
    props: Dict[str, Any] = {
        "limit": {
            "type": "integer",
            "default": default_limit,
            "description": "Max results (1-500)"
        }
    }

    if with_page:
        props["page"] = {
            "type": "integer",
            "default": 1,
            "description": "Page number (1-indexed)"
        }

    if with_status:
        props["status"] = {
            "type": status_type,
            "description": "Filter by status"
        }

    return {
        "type": "object",
        "properties": props,
        "additionalProperties": False
    }


def search_schema(
    query_description: str = "Search query",
    default_limit: int = 20
) -> Dict[str, Any]:
    """Generate a schema for search operations.

    Args:
        query_description: Description for the query parameter
        default_limit: Default limit for search results

    Returns:
        JSON Schema for search operation parameters

    Example:
        >>> search_schema("Customer name to search")
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Customer name to search"},
                "limit": {"type": "integer", "default": 20, "description": "Max results (1-100)"}
            },
            "required": ["query"],
            "additionalProperties": False
        }
    """
    return {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": query_description
            },
            "limit": {
                "type": "integer",
                "default": default_limit,
                "description": "Max results (1-100)"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }


def line_schema(entity: str) -> Dict[str, Any]:
    """Generate a schema for adding line items to invoices/proposals/orders.

    Args:
        entity: Entity type ("invoice", "proposal", or "order")

    Returns:
        JSON Schema for line item addition

    Example:
        >>> line_schema("invoice")
        {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "Invoice ID"},
                "desc": {"type": "string", "description": "Line description"},
                "qty": {"type": "number", "description": "Quantity"},
                "subprice": {"type": "number", "description": "Unit price (excl. tax)"},
                "product_id": {"type": "integer", "description": "Product ID (optional)"},
                "product_type": {"type": "integer", "default": 0, "description": "0=product, 1=service"},
                "tva_tx": {"type": "number", "description": "VAT rate (e.g., 19.0)"}
            },
            "required": ["invoice_id", "desc", "qty", "subprice"],
            "additionalProperties": False
        }
    """
    return {
        "type": "object",
        "properties": {
            f"{entity}_id": {
                "type": "integer",
                "description": f"{entity.capitalize()} ID"
            },
            "desc": {
                "type": "string",
                "description": "Line description"
            },
            "description": {
                "type": "string",
                "description": "Alias of desc"
            },
            "qty": {
                "type": "number",
                "description": "Quantity"
            },
            "subprice": {
                "type": "number",
                "description": "Unit price (excl. tax)"
            },
            "product_id": {
                "type": "integer",
                "description": "Product ID (optional)"
            },
            "product_type": {
                "type": "integer",
                "default": 0,
                "description": "0=product, 1=service"
            },
            "tva_tx": {
                "type": "number",
                "description": "VAT rate (e.g., 19.0)"
            },
            "remise_percent": {
                "type": "number",
                "description": "Discount percentage (0-100)"
            }
        },
        "required": [f"{entity}_id", "qty", "subprice"],
        "anyOf": [
            {"required": ["desc"]},
            {"required": ["description"]}
        ],
        "additionalProperties": False
    }


def empty_schema() -> Dict[str, Any]:
    """Generate an empty schema for parameter-less operations.

    Returns:
        JSON Schema with no parameters
    """
    return {
        "type": "object",
        "properties": {},
        "additionalProperties": False
    }


def update_line_schema(entity: str) -> Dict[str, Any]:
    """Generate a schema for updating line items.

    Args:
        entity: Entity type ("invoice" or "proposal")

    Returns:
        JSON Schema for line item update
    """
    return {
        "type": "object",
        "properties": {
            f"{entity}_id": {
                "type": "integer",
                "description": f"{entity.capitalize()} ID"
            },
            "line_id": {
                "type": "integer",
                "description": "Line ID to update"
            },
            "desc": {
                "type": "string",
                "description": "New line description"
            },
            "description": {
                "type": "string",
                "description": "Alias of desc"
            },
            "qty": {
                "type": "number",
                "description": "New quantity"
            },
            "subprice": {
                "type": "number",
                "description": "New unit price"
            },
            "tva_tx": {
                "type": "number",
                "description": "New VAT rate"
            },
            "remise_percent": {
                "type": "number",
                "description": "New discount percentage (0-100)"
            },
            "product_id": {
                "type": "integer",
                "description": "New linked product ID"
            },
            "product_type": {
                "type": "integer",
                "description": "0=product, 1=service"
            }
        },
        "required": [f"{entity}_id", "line_id"],
        "additionalProperties": False
    }


def delete_line_schema(entity: str) -> Dict[str, Any]:
    """Generate a schema for deleting line items.

    Args:
        entity: Entity type ("invoice" or "proposal")

    Returns:
        JSON Schema for line item deletion
    """
    return {
        "type": "object",
        "properties": {
            f"{entity}_id": {
                "type": "integer",
                "description": f"{entity.capitalize()} ID"
            },
            "line_id": {
                "type": "integer",
                "description": "Line ID to delete"
            }
        },
        "required": [f"{entity}_id", "line_id"],
        "additionalProperties": False
    }
