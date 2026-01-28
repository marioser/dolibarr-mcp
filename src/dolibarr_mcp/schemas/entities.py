"""Entity-specific schemas with full documentation.

These schemas provide detailed parameter descriptions, constraints,
and examples for AI agents to understand how to use each tool.
"""

from typing import Any, Dict

# =============================================================================
# CUSTOMER SCHEMAS
# =============================================================================

CUSTOMER_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Company or person name (required, 2-255 chars)",
            "minLength": 2,
            "maxLength": 255
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Email address (optional, must be unique if provided)"
        },
        "phone": {
            "type": "string",
            "description": "Phone number with country code (e.g., +57 300 123 4567)"
        },
        "address": {
            "type": "string",
            "description": "Street address"
        },
        "town": {
            "type": "string",
            "description": "City name"
        },
        "zip": {
            "type": "string",
            "description": "Postal/ZIP code"
        },
        "country_id": {
            "type": "integer",
            "default": 1,
            "description": "Country ID (1=France default, use Dolibarr country codes)"
        },
        "type": {
            "type": "integer",
            "enum": [1, 2, 3],
            "default": 1,
            "description": "Type: 1=customer, 2=supplier, 3=both"
        },
        "status": {
            "type": "integer",
            "enum": [0, 1],
            "default": 1,
            "description": "Status: 0=inactive, 1=active (default)"
        }
    },
    "required": ["name"],
    "additionalProperties": False
}

CUSTOMER_UPDATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_id": {
            "type": "integer",
            "description": "Customer ID to update (required)"
        },
        "name": {
            "type": "string",
            "description": "New company/person name"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "New email address"
        },
        "phone": {
            "type": "string",
            "description": "New phone number"
        },
        "address": {
            "type": "string",
            "description": "New street address"
        },
        "town": {
            "type": "string",
            "description": "New city name"
        },
        "zip": {
            "type": "string",
            "description": "New postal code"
        },
        "status": {
            "type": "integer",
            "enum": [0, 1],
            "description": "New status: 0=inactive, 1=active"
        }
    },
    "required": ["customer_id"],
    "additionalProperties": False
}

# =============================================================================
# PRODUCT SCHEMAS
# =============================================================================

PRODUCT_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "label": {
            "type": "string",
            "description": "Product name/label (required, 2-255 chars)",
            "minLength": 2,
            "maxLength": 255
        },
        "price": {
            "type": "number",
            "description": "Sale price excluding tax (required, >= 0)",
            "minimum": 0
        },
        "description": {
            "type": "string",
            "description": "Product description (optional, supports HTML)"
        },
        "stock": {
            "type": "integer",
            "description": "Initial stock quantity (optional, default 0)",
            "default": 0
        },
        "ref": {
            "type": "string",
            "description": "Product reference (auto-generated if not provided)"
        },
        "type": {
            "type": "integer",
            "enum": [0, 1],
            "default": 0,
            "description": "Product type: 0=product (default), 1=service"
        }
    },
    "required": ["label", "price"],
    "additionalProperties": False
}

PRODUCT_UPDATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "product_id": {
            "type": "integer",
            "description": "Product ID to update (required)"
        },
        "label": {
            "type": "string",
            "description": "New product name"
        },
        "price": {
            "type": "number",
            "description": "New sale price excluding tax"
        },
        "description": {
            "type": "string",
            "description": "New product description"
        }
    },
    "required": ["product_id"],
    "additionalProperties": False
}

# =============================================================================
# INVOICE SCHEMAS
# =============================================================================

INVOICE_LINE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "desc": {
            "type": "string",
            "description": "Line description (required)"
        },
        "qty": {
            "type": "number",
            "description": "Quantity (required, > 0)",
            "minimum": 0.001
        },
        "subprice": {
            "type": "number",
            "description": "Unit price excluding tax (required)",
            "minimum": 0
        },
        "product_id": {
            "type": "integer",
            "description": "Link to product (optional)"
        },
        "product_type": {
            "type": "integer",
            "enum": [0, 1],
            "description": "0=product, 1=service"
        },
        "vat": {
            "type": "number",
            "description": "VAT rate percentage (e.g., 19.0)"
        }
    },
    "required": ["desc", "qty", "subprice"]
}

INVOICE_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_id": {
            "type": "integer",
            "description": "Customer/third-party ID (required)"
        },
        "date": {
            "type": "string",
            "description": "Invoice date in YYYY-MM-DD format (optional, defaults to today)"
        },
        "due_date": {
            "type": "string",
            "description": "Payment due date in YYYY-MM-DD format (optional)"
        },
        "lines": {
            "type": "array",
            "description": "Invoice line items (at least one required)",
            "items": INVOICE_LINE_SCHEMA,
            "minItems": 1
        }
    },
    "required": ["customer_id", "lines"],
    "additionalProperties": False
}

INVOICE_UPDATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "invoice_id": {
            "type": "integer",
            "description": "Invoice ID to update (required)"
        },
        "date": {
            "type": "string",
            "description": "New invoice date (YYYY-MM-DD)"
        },
        "due_date": {
            "type": "string",
            "description": "New due date (YYYY-MM-DD)"
        }
    },
    "required": ["invoice_id"],
    "additionalProperties": False
}

INVOICE_VALIDATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "invoice_id": {
            "type": "integer",
            "description": "Invoice ID to validate (required)"
        },
        "warehouse_id": {
            "type": "integer",
            "default": 0,
            "description": "Warehouse ID for stock movements (optional)"
        }
    },
    "required": ["invoice_id"],
    "additionalProperties": False
}

# =============================================================================
# PROPOSAL SCHEMAS
# =============================================================================

PROPOSAL_LINE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "desc": {
            "type": "string",
            "description": "Line description (required)"
        },
        "qty": {
            "type": "number",
            "description": "Quantity (required)",
            "minimum": 0.001
        },
        "subprice": {
            "type": "number",
            "description": "Unit price excluding tax (required)",
            "minimum": 0
        },
        "product_id": {
            "type": "integer",
            "description": "Link to product (optional)"
        },
        "product_type": {
            "type": "integer",
            "enum": [0, 1],
            "description": "0=product, 1=service"
        },
        "tva_tx": {
            "type": "number",
            "description": "VAT rate percentage"
        },
        "remise_percent": {
            "type": "number",
            "description": "Discount percentage (0-100)"
        }
    },
    "required": ["desc", "qty", "subprice"]
}

PROPOSAL_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_id": {
            "type": "integer",
            "description": "Customer/third-party ID (required)"
        },
        "date": {
            "type": "string",
            "description": "Proposal date in YYYY-MM-DD format (optional)"
        },
        "duree_validite": {
            "type": "integer",
            "default": 30,
            "description": "Validity period in days (default 30)"
        },
        "project_id": {
            "type": "integer",
            "description": "Link to project (optional)"
        },
        "note_public": {
            "type": "string",
            "description": "Public notes (visible to customer)"
        },
        "note_private": {
            "type": "string",
            "description": "Private/internal notes"
        },
        "lines": {
            "type": "array",
            "description": "Proposal line items (optional)",
            "items": PROPOSAL_LINE_SCHEMA
        }
    },
    "required": ["customer_id"],
    "additionalProperties": False
}

# =============================================================================
# USER SCHEMAS
# =============================================================================

USER_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "login": {
            "type": "string",
            "description": "Username for login (required, unique, 3-50 chars)",
            "minLength": 3,
            "maxLength": 50
        },
        "lastname": {
            "type": "string",
            "description": "User's last name (required)"
        },
        "firstname": {
            "type": "string",
            "description": "User's first name (optional)"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "User's email address"
        },
        "password": {
            "type": "string",
            "description": "Initial password (optional, min 8 chars recommended)"
        },
        "admin": {
            "type": "integer",
            "enum": [0, 1],
            "default": 0,
            "description": "Admin privileges: 0=no (default), 1=yes"
        }
    },
    "required": ["login", "lastname"],
    "additionalProperties": False
}

USER_UPDATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "integer",
            "description": "User ID to update (required)"
        },
        "login": {
            "type": "string",
            "description": "New username"
        },
        "lastname": {
            "type": "string",
            "description": "New last name"
        },
        "firstname": {
            "type": "string",
            "description": "New first name"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "New email address"
        },
        "admin": {
            "type": "integer",
            "enum": [0, 1],
            "description": "Admin privileges: 0=no, 1=yes"
        }
    },
    "required": ["user_id"],
    "additionalProperties": False
}

# =============================================================================
# PROJECT SCHEMAS
# =============================================================================

PROJECT_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Project title (required)"
        },
        "ref": {
            "type": "string",
            "description": "Project reference (auto-generated if not provided)"
        },
        "description": {
            "type": "string",
            "description": "Project description"
        },
        "socid": {
            "type": "integer",
            "description": "Customer/third-party ID to link"
        },
        "status": {
            "type": "integer",
            "enum": [0, 1, 2],
            "default": 1,
            "description": "Status: 0=draft, 1=open (default), 2=closed"
        }
    },
    "required": ["title"],
    "additionalProperties": False
}

# =============================================================================
# CONTACT SCHEMAS
# =============================================================================

CONTACT_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "firstname": {
            "type": "string",
            "description": "Contact's first name (required)"
        },
        "lastname": {
            "type": "string",
            "description": "Contact's last name (required)"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Contact's email address"
        },
        "phone": {
            "type": "string",
            "description": "Contact's phone number"
        },
        "socid": {
            "type": "integer",
            "description": "Link to customer/third-party"
        }
    },
    "required": ["firstname", "lastname"],
    "additionalProperties": False
}

# =============================================================================
# ORDER SCHEMAS
# =============================================================================

ORDER_CREATE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_id": {
            "type": "integer",
            "description": "Customer/third-party ID (required)"
        },
        "date": {
            "type": "string",
            "description": "Order date in YYYY-MM-DD format (optional)"
        }
    },
    "required": ["customer_id"],
    "additionalProperties": False
}

# =============================================================================
# RAW API SCHEMA
# =============================================================================

RAW_API_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE"],
            "description": "HTTP method"
        },
        "endpoint": {
            "type": "string",
            "description": "API endpoint path (e.g., 'thirdparties', 'invoices/123')"
        },
        "params": {
            "type": "object",
            "description": "Query parameters (optional)"
        },
        "data": {
            "type": "object",
            "description": "Request body for POST/PUT (optional)"
        }
    },
    "required": ["method", "endpoint"],
    "additionalProperties": False
}
