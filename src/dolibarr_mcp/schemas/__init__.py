"""Schema definitions for Dolibarr MCP tools."""

from .base import id_schema, list_schema, search_schema, line_schema
from .fields import (
    CUSTOMER_FIELDS,
    PRODUCT_FIELDS,
    INVOICE_FIELDS,
    ORDER_FIELDS,
    PROPOSAL_FIELDS,
    PROJECT_FIELDS,
    CONTACT_FIELDS,
    USER_FIELDS,
    LINE_FIELDS,
)
from .entities import (
    CUSTOMER_CREATE_SCHEMA,
    CUSTOMER_UPDATE_SCHEMA,
    PRODUCT_CREATE_SCHEMA,
    INVOICE_CREATE_SCHEMA,
    PROPOSAL_CREATE_SCHEMA,
    PROPOSAL_UPDATE_SCHEMA,
)

__all__ = [
    # Schema helpers
    "id_schema",
    "list_schema",
    "search_schema",
    "line_schema",
    # Field definitions
    "CUSTOMER_FIELDS",
    "PRODUCT_FIELDS",
    "INVOICE_FIELDS",
    "ORDER_FIELDS",
    "PROPOSAL_FIELDS",
    "PROJECT_FIELDS",
    "CONTACT_FIELDS",
    "USER_FIELDS",
    "LINE_FIELDS",
    # Entity schemas
    "CUSTOMER_CREATE_SCHEMA",
    "CUSTOMER_UPDATE_SCHEMA",
    "PRODUCT_CREATE_SCHEMA",
    "INVOICE_CREATE_SCHEMA",
    "PROPOSAL_CREATE_SCHEMA",
    "PROPOSAL_UPDATE_SCHEMA",
]
