"""Tool registry and definitions for Dolibarr MCP Server.

This module implements a declarative tool registry that replaces
the 59 if-statements in the original dispatcher with a single lookup table.

Each tool definition includes:
- method: Client method name to call
- fields: Response field filter (or None for create/delete operations)
- description: AI-optimized description with format:
  [ACTION] [OBJECT]. [FIELDS RETURNED]. [CONSTRAINTS/NOTES].
- schema: JSON Schema for input parameters
- id_param: Parameter name to extract as first positional arg (optional)
- paginated: Whether to wrap response with pagination metadata
"""

from typing import Any, Dict, List, Optional, Callable

from ..schemas.base import (
    id_schema,
    list_schema,
    search_schema,
    line_schema,
    empty_schema,
    update_line_schema,
    delete_line_schema,
)
from ..schemas.fields import (
    CUSTOMER_FIELDS,
    PRODUCT_FIELDS,
    INVOICE_FIELDS,
    ORDER_FIELDS,
    PROPOSAL_FIELDS,
    PROJECT_FIELDS,
    CONTACT_FIELDS,
    USER_FIELDS,
)
from ..schemas.entities import (
    CUSTOMER_CREATE_SCHEMA,
    CUSTOMER_UPDATE_SCHEMA,
    PRODUCT_CREATE_SCHEMA,
    PRODUCT_UPDATE_SCHEMA,
    INVOICE_CREATE_SCHEMA,
    INVOICE_UPDATE_SCHEMA,
    PROPOSAL_CREATE_SCHEMA,
    USER_CREATE_SCHEMA,
    USER_UPDATE_SCHEMA,
    PROJECT_CREATE_SCHEMA,
    CONTACT_CREATE_SCHEMA,
    ORDER_CREATE_SCHEMA,
    RAW_API_SCHEMA,
)


# =============================================================================
# TOOL REGISTRY
# =============================================================================

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # SYSTEM TOOLS
    # =========================================================================
    "test_connection": {
        "method": "get_status",
        "fields": None,
        "description": "Test Dolibarr API connection. Returns version info if connected. Use to verify API is reachable.",
        "schema": empty_schema(),
        "paginated": False,
    },
    "get_status": {
        "method": "get_status",
        "fields": None,
        "description": "Get Dolibarr system status. Returns dolibarr_version, api_version. Use to check API health.",
        "schema": empty_schema(),
        "paginated": False,
    },

    # =========================================================================
    # SEARCH TOOLS
    # =========================================================================
    "search_products_by_ref": {
        "method": "search_products",
        "fields": PRODUCT_FIELDS,
        "description": "Search products by reference prefix. Returns id, ref, label, price, status. Max 20 results. Case-insensitive prefix match.",
        "schema": {
            "type": "object",
            "properties": {
                "ref_prefix": {"type": "string", "description": "Reference prefix to match (e.g., 'PROD' matches 'PROD001')"},
                "limit": {"type": "integer", "default": 20, "description": "Max results (1-100)"}
            },
            "required": ["ref_prefix"],
            "additionalProperties": False
        },
        "paginated": True,
        "search_handler": "ref_prefix",  # Special handler for search
    },
    "search_products_by_label": {
        "method": "search_products",
        "fields": PRODUCT_FIELDS,
        "description": "Search products by label/name. Returns id, ref, label, price, status. Max 20 results. Partial match supported.",
        "schema": search_schema("Product name to search (partial match)"),
        "paginated": True,
        "search_handler": "label",
    },
    "search_customers": {
        "method": "search_customers",
        "fields": CUSTOMER_FIELDS,
        "description": "Search customers by name or alias. Returns id, name, email, phone, status. Max 20 results. Partial match on name and name_alias.",
        "schema": search_schema("Customer name to search (partial match)"),
        "paginated": True,
        "search_handler": "customer",
    },
    "resolve_product_ref": {
        "method": "search_products",
        "fields": PRODUCT_FIELDS,
        "description": "Get exact product by reference. Returns status: 'ok' (found), 'not_found', or 'ambiguous' (multiple matches). Use for exact ref lookup.",
        "schema": {
            "type": "object",
            "properties": {"ref": {"type": "string", "description": "Exact product reference"}},
            "required": ["ref"],
            "additionalProperties": False
        },
        "paginated": False,
        "search_handler": "resolve_ref",
    },
    "search_projects": {
        "method": "search_projects",
        "fields": PROJECT_FIELDS,
        "description": "Search projects by ref or title. Returns id, ref, title, status, socid. Max 20 results. Partial match.",
        "schema": search_schema("Project ref or title to search"),
        "paginated": True,
        "search_handler": "project",
    },
    "search_proposals": {
        "method": "search_proposals",
        "fields": PROPOSAL_FIELDS,
        "description": "Search proposals by ref or customer name. Returns id, ref, socid, total_ttc, status. Max 20 results.",
        "schema": search_schema("Proposal ref or customer name to search"),
        "paginated": True,
        "search_handler": "proposal",
    },

    # =========================================================================
    # USER TOOLS
    # =========================================================================
    "get_users": {
        "method": "get_users",
        "fields": USER_FIELDS,
        "description": "List users with pagination. Returns id, login, lastname, firstname, email, admin, status. Use page param for pagination.",
        "schema": list_schema(with_page=True),
        "paginated": True,
    },
    "get_user_by_id": {
        "method": "get_user_by_id",
        "fields": USER_FIELDS,
        "description": "Get user by ID. Returns id, login, lastname, firstname, email, admin, status. Use for user details.",
        "schema": id_schema("user_id", "User ID to retrieve"),
        "id_param": "user_id",
        "paginated": False,
    },
    "create_user": {
        "method": "create_user",
        "fields": None,
        "description": "Create user. Required: login (unique), lastname. Optional: firstname, email, password, admin (0/1). Returns new user ID.",
        "schema": USER_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_user": {
        "method": "update_user",
        "fields": None,
        "description": "Update user. Required: user_id. Optional: login, lastname, firstname, email, admin. Returns update confirmation.",
        "schema": USER_UPDATE_SCHEMA,
        "id_param": "user_id",
        "paginated": False,
    },
    "delete_user": {
        "method": "delete_user",
        "fields": None,
        "description": "Delete user by ID. Returns deletion confirmation. Cannot be undone.",
        "schema": id_schema("user_id", "User ID to delete"),
        "id_param": "user_id",
        "paginated": False,
    },

    # =========================================================================
    # CUSTOMER TOOLS
    # =========================================================================
    "get_customers": {
        "method": "get_customers",
        "fields": CUSTOMER_FIELDS,
        "description": "List customers with pagination. Returns id, name, email, phone, address, status. Use page param for large lists.",
        "schema": list_schema(with_page=True),
        "paginated": True,
    },
    "get_customer_by_id": {
        "method": "get_customer_by_id",
        "fields": CUSTOMER_FIELDS,
        "description": "Get customer by ID. Returns id, name, email, phone, address, town, zip, status. Use for customer details.",
        "schema": id_schema("customer_id", "Customer ID to retrieve"),
        "id_param": "customer_id",
        "paginated": False,
    },
    "create_customer": {
        "method": "create_customer",
        "fields": None,
        "description": "Create customer. Required: name. Optional: email (unique), phone, address, town, zip, country_id, type (1=customer), status. Returns new ID.",
        "schema": CUSTOMER_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_customer": {
        "method": "update_customer",
        "fields": None,
        "description": "Update customer. Required: customer_id. Optional: name, email, phone, address, town, zip, status. Returns update confirmation.",
        "schema": CUSTOMER_UPDATE_SCHEMA,
        "id_param": "customer_id",
        "paginated": False,
    },
    "delete_customer": {
        "method": "delete_customer",
        "fields": None,
        "description": "Delete customer by ID. Returns deletion confirmation. Cannot be undone. Fails if customer has linked documents.",
        "schema": id_schema("customer_id", "Customer ID to delete"),
        "id_param": "customer_id",
        "paginated": False,
    },

    # =========================================================================
    # PRODUCT TOOLS
    # =========================================================================
    "get_products": {
        "method": "get_products",
        "fields": PRODUCT_FIELDS,
        "description": "List products. Returns id, ref, label, price, price_ttc, type, status, stock_reel. Max 100 results.",
        "schema": list_schema(),
        "paginated": True,
    },
    "get_product_by_id": {
        "method": "get_product_by_id",
        "fields": PRODUCT_FIELDS,
        "description": "Get product by ID. Returns id, ref, label, description, price, price_ttc, type, status, stock_reel, barcode.",
        "schema": id_schema("product_id", "Product ID to retrieve"),
        "id_param": "product_id",
        "paginated": False,
    },
    "create_product": {
        "method": "create_product",
        "fields": None,
        "description": "Create product. Required: label, price. Optional: description, stock. Auto-generates ref if not provided. Returns new product ID.",
        "schema": PRODUCT_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_product": {
        "method": "update_product",
        "fields": None,
        "description": "Update product. Required: product_id. Optional: label, price, description. Returns update confirmation.",
        "schema": PRODUCT_UPDATE_SCHEMA,
        "id_param": "product_id",
        "paginated": False,
    },
    "delete_product": {
        "method": "delete_product",
        "fields": None,
        "description": "Delete product by ID. Returns deletion confirmation. Cannot be undone. Fails if product has linked documents.",
        "schema": id_schema("product_id", "Product ID to delete"),
        "id_param": "product_id",
        "paginated": False,
    },

    # =========================================================================
    # INVOICE TOOLS
    # =========================================================================
    "get_invoices": {
        "method": "get_invoices",
        "fields": INVOICE_FIELDS,
        "description": "List invoices. Filter by status: draft, unpaid, paid. Returns id, ref, socid, date, total_ttc, status, lines.",
        "schema": list_schema(with_status=True, status_type="string"),
        "paginated": True,
    },
    "get_invoice_by_id": {
        "method": "get_invoice_by_id",
        "fields": INVOICE_FIELDS,
        "description": "Get invoice by ID. Returns id, ref, socid, date, due_date, total_ht, total_tva, total_ttc, paye, status, lines.",
        "schema": id_schema("invoice_id", "Invoice ID to retrieve"),
        "id_param": "invoice_id",
        "paginated": False,
    },
    "create_invoice": {
        "method": "create_invoice",
        "fields": None,
        "description": "Create invoice with lines. Required: customer_id, lines[]. Optional: date, due_date. Each line needs desc, qty, subprice. Returns new invoice ID.",
        "schema": INVOICE_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_invoice": {
        "method": "update_invoice",
        "fields": None,
        "description": "Update invoice. Required: invoice_id. Optional: date, due_date. Only draft invoices can be modified.",
        "schema": INVOICE_UPDATE_SCHEMA,
        "id_param": "invoice_id",
        "paginated": False,
    },
    "delete_invoice": {
        "method": "delete_invoice",
        "fields": None,
        "description": "Delete invoice by ID. Returns deletion confirmation. Only draft invoices can be deleted.",
        "schema": id_schema("invoice_id", "Invoice ID to delete"),
        "id_param": "invoice_id",
        "paginated": False,
    },
    "add_invoice_line": {
        "method": "add_invoice_line",
        "fields": None,
        "description": "Add line to invoice. Required: invoice_id, desc, qty, subprice. Optional: product_id, product_type (0=product,1=service), tva_tx.",
        "schema": line_schema("invoice"),
        "id_param": "invoice_id",
        "paginated": False,
    },
    "update_invoice_line": {
        "method": "update_invoice_line",
        "fields": None,
        "description": "Update invoice line. Required: invoice_id, line_id. Optional: desc, qty, subprice, vat. Only draft invoices.",
        "schema": update_line_schema("invoice"),
        "id_param": "invoice_id",
        "line_param": "line_id",
        "paginated": False,
    },
    "delete_invoice_line": {
        "method": "delete_invoice_line",
        "fields": None,
        "description": "Delete invoice line. Required: invoice_id, line_id. Only draft invoices. Returns deletion confirmation.",
        "schema": delete_line_schema("invoice"),
        "id_param": "invoice_id",
        "line_param": "line_id",
        "paginated": False,
    },
    "validate_invoice": {
        "method": "validate_invoice",
        "fields": None,
        "description": "Validate draft invoice. Required: invoice_id. Optional: warehouse_id (for stock). Changes status from draft to validated.",
        "schema": {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "integer", "description": "Invoice ID to validate"},
                "warehouse_id": {"type": "integer", "default": 0, "description": "Warehouse ID for stock movements"}
            },
            "required": ["invoice_id"],
            "additionalProperties": False
        },
        "id_param": "invoice_id",
        "paginated": False,
    },

    # =========================================================================
    # ORDER TOOLS
    # =========================================================================
    "get_orders": {
        "method": "get_orders",
        "fields": ORDER_FIELDS,
        "description": "List orders. Filter by status. Returns id, ref, socid, date, total_ht, total_ttc, status, lines.",
        "schema": list_schema(with_status=True),
        "paginated": True,
    },
    "get_order_by_id": {
        "method": "get_order_by_id",
        "fields": ORDER_FIELDS,
        "description": "Get order by ID. Returns id, ref, socid, date, total_ht, total_ttc, status, lines.",
        "schema": id_schema("order_id", "Order ID to retrieve"),
        "id_param": "order_id",
        "paginated": False,
    },
    "create_order": {
        "method": "create_order",
        "fields": None,
        "description": "Create order. Required: customer_id. Optional: date. Returns new order ID. Add lines separately.",
        "schema": ORDER_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_order": {
        "method": "update_order",
        "fields": None,
        "description": "Update order. Required: order_id. Optional: date. Only draft orders can be modified.",
        "schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to update"},
                "date": {"type": "string", "description": "New order date (YYYY-MM-DD)"}
            },
            "required": ["order_id"],
            "additionalProperties": False
        },
        "id_param": "order_id",
        "paginated": False,
    },
    "delete_order": {
        "method": "delete_order",
        "fields": None,
        "description": "Delete order by ID. Returns deletion confirmation. Only draft orders can be deleted.",
        "schema": id_schema("order_id", "Order ID to delete"),
        "id_param": "order_id",
        "paginated": False,
    },

    # =========================================================================
    # CONTACT TOOLS
    # =========================================================================
    "get_contacts": {
        "method": "get_contacts",
        "fields": CONTACT_FIELDS,
        "description": "List contacts. Returns id, firstname, lastname, email, phone, socid. Max 100 results.",
        "schema": list_schema(),
        "paginated": True,
    },
    "get_contact_by_id": {
        "method": "get_contact_by_id",
        "fields": CONTACT_FIELDS,
        "description": "Get contact by ID. Returns id, firstname, lastname, email, phone, socid.",
        "schema": id_schema("contact_id", "Contact ID to retrieve"),
        "id_param": "contact_id",
        "paginated": False,
    },
    "create_contact": {
        "method": "create_contact",
        "fields": None,
        "description": "Create contact. Required: firstname, lastname. Optional: email, phone, socid (link to customer). Returns new contact ID.",
        "schema": CONTACT_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_contact": {
        "method": "update_contact",
        "fields": None,
        "description": "Update contact. Required: contact_id. Optional: firstname, lastname, email, phone. Returns update confirmation.",
        "schema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "integer", "description": "Contact ID to update"},
                "firstname": {"type": "string", "description": "New first name"},
                "lastname": {"type": "string", "description": "New last name"},
                "email": {"type": "string", "description": "New email"},
                "phone": {"type": "string", "description": "New phone"}
            },
            "required": ["contact_id"],
            "additionalProperties": False
        },
        "id_param": "contact_id",
        "paginated": False,
    },
    "delete_contact": {
        "method": "delete_contact",
        "fields": None,
        "description": "Delete contact by ID. Returns deletion confirmation. Cannot be undone.",
        "schema": id_schema("contact_id", "Contact ID to delete"),
        "id_param": "contact_id",
        "paginated": False,
    },

    # =========================================================================
    # PROJECT TOOLS
    # =========================================================================
    "get_projects": {
        "method": "get_projects",
        "fields": PROJECT_FIELDS,
        "description": "List projects. Filter by status: 0=draft, 1=open, 2=closed. Returns id, ref, title, description, socid, status, dates.",
        "schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 100, "description": "Max results"},
                "page": {"type": "integer", "default": 1, "description": "Page number"},
                "status": {"type": "integer", "default": 1, "description": "Status: 0=draft, 1=open, 2=closed"}
            },
            "additionalProperties": False
        },
        "paginated": True,
    },
    "get_project_by_id": {
        "method": "get_project_by_id",
        "fields": PROJECT_FIELDS,
        "description": "Get project by ID. Returns id, ref, title, description, socid, status, date_start, date_end.",
        "schema": id_schema("project_id", "Project ID to retrieve"),
        "id_param": "project_id",
        "paginated": False,
    },
    "create_project": {
        "method": "create_project",
        "fields": None,
        "description": "Create project. Required: title. Optional: ref (auto-gen), description, socid, status (default 1=open). Returns new project ID.",
        "schema": PROJECT_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_project": {
        "method": "update_project",
        "fields": None,
        "description": "Update project. Required: project_id. Optional: title, description, status (0=draft, 1=open, 2=closed).",
        "schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "Project ID to update"},
                "title": {"type": "string", "description": "New title"},
                "description": {"type": "string", "description": "New description"},
                "status": {"type": "integer", "description": "New status: 0=draft, 1=open, 2=closed"}
            },
            "required": ["project_id"],
            "additionalProperties": False
        },
        "id_param": "project_id",
        "paginated": False,
    },
    "delete_project": {
        "method": "delete_project",
        "fields": None,
        "description": "Delete project by ID. Returns deletion confirmation. Fails if project has linked documents.",
        "schema": id_schema("project_id", "Project ID to delete"),
        "id_param": "project_id",
        "paginated": False,
    },

    # =========================================================================
    # PROPOSAL TOOLS
    # =========================================================================
    "get_proposals": {
        "method": "get_proposals",
        "fields": PROPOSAL_FIELDS,
        "description": "List proposals/quotes. Filter by status: 0=draft, 1=validated, 2=signed, 3=refused. Returns id, ref, socid, totals, status, lines.",
        "schema": list_schema(with_status=True, status_type="integer"),
        "paginated": True,
    },
    "get_proposal_by_id": {
        "method": "get_proposal_by_id",
        "fields": PROPOSAL_FIELDS,
        "description": "Get proposal by ID. Returns id, ref, socid, date, fin_validite, total_ht, total_tva, total_ttc, status, lines.",
        "schema": id_schema("proposal_id", "Proposal ID to retrieve"),
        "id_param": "proposal_id",
        "paginated": False,
    },
    "create_proposal": {
        "method": "create_proposal",
        "fields": None,
        "description": "Create proposal/quote. Required: customer_id. Optional: lines[], date, duree_validite (days), project_id, notes. Returns new proposal ID.",
        "schema": PROPOSAL_CREATE_SCHEMA,
        "paginated": False,
    },
    "update_proposal": {
        "method": "update_proposal",
        "fields": None,
        "description": "Update draft proposal. Required: proposal_id. Optional: duree_validite, note_public, note_private. Only drafts can be modified.",
        "schema": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "integer", "description": "Proposal ID to update"},
                "duree_validite": {"type": "integer", "description": "Validity period in days"},
                "note_public": {"type": "string", "description": "Public notes (visible to customer)"},
                "note_private": {"type": "string", "description": "Private/internal notes"}
            },
            "required": ["proposal_id"],
            "additionalProperties": False
        },
        "id_param": "proposal_id",
        "paginated": False,
    },
    "delete_proposal": {
        "method": "delete_proposal",
        "fields": None,
        "description": "Delete proposal by ID. Returns deletion confirmation. Only drafts can be deleted.",
        "schema": id_schema("proposal_id", "Proposal ID to delete"),
        "id_param": "proposal_id",
        "paginated": False,
    },
    "add_proposal_line": {
        "method": "add_proposal_line",
        "fields": None,
        "description": "Add line to proposal. Required: proposal_id, desc, qty, subprice. Optional: product_id, product_type, tva_tx. Only drafts.",
        "schema": line_schema("proposal"),
        "id_param": "proposal_id",
        "paginated": False,
    },
    "update_proposal_line": {
        "method": "update_proposal_line",
        "fields": None,
        "description": "Update proposal line. Required: proposal_id, line_id. Optional: desc, qty, subprice, tva_tx. Only drafts.",
        "schema": update_line_schema("proposal"),
        "id_param": "proposal_id",
        "line_param": "line_id",
        "paginated": False,
    },
    "delete_proposal_line": {
        "method": "delete_proposal_line",
        "fields": None,
        "description": "Delete proposal line. Required: proposal_id, line_id. Only drafts. Returns deletion confirmation.",
        "schema": delete_line_schema("proposal"),
        "id_param": "proposal_id",
        "line_param": "line_id",
        "paginated": False,
    },
    "validate_proposal": {
        "method": "validate_proposal",
        "fields": None,
        "description": "Validate draft proposal. Required: proposal_id. Changes status from draft (0) to validated (1).",
        "schema": id_schema("proposal_id", "Proposal ID to validate"),
        "id_param": "proposal_id",
        "paginated": False,
    },
    "close_proposal": {
        "method": "close_proposal",
        "fields": None,
        "description": "Close proposal as signed or refused. Required: proposal_id, status (2=signed/won, 3=refused/lost). Optional: note.",
        "schema": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "integer", "description": "Proposal ID to close"},
                "status": {"type": "integer", "enum": [2, 3], "description": "Close status: 2=signed/won, 3=refused/lost"},
                "note": {"type": "string", "description": "Closing note (optional)"}
            },
            "required": ["proposal_id", "status"],
            "additionalProperties": False
        },
        "id_param": "proposal_id",
        "paginated": False,
    },
    "set_proposal_to_draft": {
        "method": "set_proposal_to_draft",
        "fields": None,
        "description": "Revert proposal to draft status. Required: proposal_id. Allows re-editing a validated proposal.",
        "schema": id_schema("proposal_id", "Proposal ID to revert to draft"),
        "id_param": "proposal_id",
        "paginated": False,
    },

    # =========================================================================
    # RAW API TOOL
    # =========================================================================
    "dolibarr_raw_api": {
        "method": "dolibarr_raw_api",
        "fields": None,
        "description": "Direct API call. Use only if no specific tool exists. Required: method (GET/POST/PUT/DELETE), endpoint. Optional: params, data.",
        "schema": RAW_API_SCHEMA,
        "paginated": False,
    },
}


def get_tool_names() -> List[str]:
    """Get list of all registered tool names."""
    return list(TOOL_REGISTRY.keys())


def get_tool_definition(name: str) -> Optional[Dict[str, Any]]:
    """Get tool definition by name."""
    return TOOL_REGISTRY.get(name)


def get_tool_schema(name: str) -> Optional[Dict[str, Any]]:
    """Get tool input schema by name."""
    tool = TOOL_REGISTRY.get(name)
    return tool["schema"] if tool else None


def get_tool_description(name: str) -> Optional[str]:
    """Get tool description by name."""
    tool = TOOL_REGISTRY.get(name)
    return tool["description"] if tool else None
