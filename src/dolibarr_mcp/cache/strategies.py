"""Cache strategies and TTL configuration for Dolibarr entities.

Different entities have different caching requirements based on
how frequently they change and how often they're accessed.
"""

from enum import Enum
from typing import Dict, Optional


class CacheStrategy(Enum):
    """Cache strategy types."""

    # No caching - always fetch fresh
    NO_CACHE = 0

    # Short TTL for frequently changing data
    SHORT = 30  # 30 seconds

    # Medium TTL for semi-static data
    MEDIUM = 300  # 5 minutes

    # Long TTL for rarely changing data
    LONG = 900  # 15 minutes

    # Very long TTL for static reference data
    STATIC = 3600  # 1 hour

    # Extended TTL for rarely changing data
    EXTENDED = 1800  # 30 minutes


# Entity-specific cache strategies
ENTITY_STRATEGIES: Dict[str, CacheStrategy] = {
    # System - short cache for health checks
    "test_connection": CacheStrategy.SHORT,
    "get_status": CacheStrategy.SHORT,

    # Products - relatively static, cache 30 min
    "get_products": CacheStrategy.EXTENDED,
    "get_product_by_id": CacheStrategy.EXTENDED,
    "search_products_by_ref": CacheStrategy.LONG,
    "search_products_by_label": CacheStrategy.LONG,
    "resolve_product_ref": CacheStrategy.LONG,

    # Customers - semi-static
    "get_customers": CacheStrategy.MEDIUM,
    "get_customer_by_id": CacheStrategy.MEDIUM,
    "search_customers": CacheStrategy.MEDIUM,

    # Users - semi-static
    "get_users": CacheStrategy.MEDIUM,
    "get_user_by_id": CacheStrategy.MEDIUM,

    # Contacts - semi-static
    "get_contacts": CacheStrategy.MEDIUM,
    "get_contact_by_id": CacheStrategy.MEDIUM,

    # Projects - long cache (15 min)
    "get_projects": CacheStrategy.LONG,
    "get_project_by_id": CacheStrategy.LONG,
    "search_projects": CacheStrategy.LONG,

    # Invoices - medium cache (5 min)
    "get_invoices": CacheStrategy.MEDIUM,
    "get_customer_invoices": CacheStrategy.MEDIUM,
    "get_invoice_by_id": CacheStrategy.MEDIUM,

    # Orders - medium cache (5 min)
    "get_orders": CacheStrategy.MEDIUM,
    "get_customer_orders": CacheStrategy.MEDIUM,
    "get_order_by_id": CacheStrategy.MEDIUM,

    # Proposals - medium cache (5 min)
    "get_proposals": CacheStrategy.MEDIUM,
    "get_customer_proposals": CacheStrategy.MEDIUM,
    "get_proposal_by_id": CacheStrategy.MEDIUM,
    "search_proposals": CacheStrategy.MEDIUM,

    # Write operations - never cache
    "create_customer": CacheStrategy.NO_CACHE,
    "update_customer": CacheStrategy.NO_CACHE,
    "delete_customer": CacheStrategy.NO_CACHE,
    "create_product": CacheStrategy.NO_CACHE,
    "update_product": CacheStrategy.NO_CACHE,
    "delete_product": CacheStrategy.NO_CACHE,
    "create_invoice": CacheStrategy.NO_CACHE,
    "update_invoice": CacheStrategy.NO_CACHE,
    "delete_invoice": CacheStrategy.NO_CACHE,
    "add_invoice_line": CacheStrategy.NO_CACHE,
    "update_invoice_line": CacheStrategy.NO_CACHE,
    "delete_invoice_line": CacheStrategy.NO_CACHE,
    "validate_invoice": CacheStrategy.NO_CACHE,
    "create_order": CacheStrategy.NO_CACHE,
    "update_order": CacheStrategy.NO_CACHE,
    "delete_order": CacheStrategy.NO_CACHE,
    "create_contact": CacheStrategy.NO_CACHE,
    "update_contact": CacheStrategy.NO_CACHE,
    "delete_contact": CacheStrategy.NO_CACHE,
    "create_project": CacheStrategy.NO_CACHE,
    "update_project": CacheStrategy.NO_CACHE,
    "delete_project": CacheStrategy.NO_CACHE,
    "create_proposal": CacheStrategy.NO_CACHE,
    "update_proposal": CacheStrategy.NO_CACHE,
    "append_proposal_note": CacheStrategy.NO_CACHE,
    "delete_proposal": CacheStrategy.NO_CACHE,
    "add_proposal_line": CacheStrategy.NO_CACHE,
    "update_proposal_line": CacheStrategy.NO_CACHE,
    "delete_proposal_line": CacheStrategy.NO_CACHE,
    "validate_proposal": CacheStrategy.NO_CACHE,
    "close_proposal": CacheStrategy.NO_CACHE,
    "set_proposal_to_draft": CacheStrategy.NO_CACHE,
    "create_user": CacheStrategy.NO_CACHE,
    "update_user": CacheStrategy.NO_CACHE,
    "delete_user": CacheStrategy.NO_CACHE,
    "dolibarr_raw_api": CacheStrategy.NO_CACHE,
}

# Tools that should invalidate related caches when called
INVALIDATION_MAP: Dict[str, list] = {
    # Customer mutations invalidate customer caches
    "create_customer": ["get_customers", "search_customers"],
    "update_customer": ["get_customers", "get_customer_by_id", "search_customers"],
    "delete_customer": ["get_customers", "get_customer_by_id", "search_customers"],

    # Product mutations invalidate product caches
    "create_product": ["get_products", "search_products_by_ref", "search_products_by_label"],
    "update_product": ["get_products", "get_product_by_id", "search_products_by_ref", "search_products_by_label", "resolve_product_ref"],
    "delete_product": ["get_products", "get_product_by_id", "search_products_by_ref", "search_products_by_label", "resolve_product_ref"],

    # Invoice mutations
    "create_invoice": ["get_invoices", "get_customer_invoices"],
    "update_invoice": ["get_invoices", "get_customer_invoices", "get_invoice_by_id"],
    "delete_invoice": ["get_invoices", "get_customer_invoices", "get_invoice_by_id"],
    "add_invoice_line": ["get_invoice_by_id"],
    "update_invoice_line": ["get_invoice_by_id"],
    "delete_invoice_line": ["get_invoice_by_id"],
    "validate_invoice": ["get_invoices", "get_customer_invoices", "get_invoice_by_id"],

    # Proposal mutations
    "create_proposal": ["get_proposals", "get_customer_proposals", "search_proposals"],
    "update_proposal": ["get_proposals", "get_customer_proposals", "get_proposal_by_id", "search_proposals"],
    "append_proposal_note": ["get_proposal_by_id"],
    "delete_proposal": ["get_proposals", "get_customer_proposals", "get_proposal_by_id", "search_proposals"],
    "add_proposal_line": ["get_proposal_by_id"],
    "update_proposal_line": ["get_proposal_by_id"],
    "delete_proposal_line": ["get_proposal_by_id"],
    "validate_proposal": ["get_proposals", "get_customer_proposals", "get_proposal_by_id"],
    "close_proposal": ["get_proposals", "get_customer_proposals", "get_proposal_by_id"],
    "set_proposal_to_draft": ["get_proposals", "get_customer_proposals", "get_proposal_by_id"],

    # Project mutations
    "create_project": ["get_projects", "search_projects"],
    "update_project": ["get_projects", "get_project_by_id", "search_projects"],
    "delete_project": ["get_projects", "get_project_by_id", "search_projects"],

    # User mutations
    "create_user": ["get_users"],
    "update_user": ["get_users", "get_user_by_id"],
    "delete_user": ["get_users", "get_user_by_id"],

    # Contact mutations
    "create_contact": ["get_contacts"],
    "update_contact": ["get_contacts", "get_contact_by_id"],
    "delete_contact": ["get_contacts", "get_contact_by_id"],

    # Order mutations
    "create_order": ["get_orders", "get_customer_orders"],
    "update_order": ["get_orders", "get_customer_orders", "get_order_by_id"],
    "delete_order": ["get_orders", "get_customer_orders", "get_order_by_id"],
}


def get_ttl_for_entity(tool_name: str) -> int:
    """Get TTL in seconds for a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        TTL in seconds, or 0 for no cache
    """
    strategy = ENTITY_STRATEGIES.get(tool_name, CacheStrategy.NO_CACHE)
    return strategy.value


def should_cache(tool_name: str) -> bool:
    """Check if a tool's results should be cached.

    Args:
        tool_name: Name of the tool

    Returns:
        True if results should be cached
    """
    strategy = ENTITY_STRATEGIES.get(tool_name, CacheStrategy.NO_CACHE)
    return strategy != CacheStrategy.NO_CACHE


def get_invalidation_targets(tool_name: str) -> list:
    """Get list of cache keys to invalidate when a tool is called.

    Args:
        tool_name: Name of the mutation tool

    Returns:
        List of tool name patterns to invalidate
    """
    return INVALIDATION_MAP.get(tool_name, [])


def is_read_operation(tool_name: str) -> bool:
    """Check if a tool is a read operation (cacheable).

    Args:
        tool_name: Name of the tool

    Returns:
        True if it's a read operation
    """
    write_prefixes = ("create_", "update_", "delete_", "add_", "validate_", "close_", "set_")
    return not any(tool_name.startswith(prefix) for prefix in write_prefixes)
