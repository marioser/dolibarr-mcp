"""Tests for DragonflyDB cache module."""

import pytest

from dolibarr_mcp.cache.strategies import (
    CacheStrategy,
    get_ttl_for_entity,
    should_cache,
    get_invalidation_targets,
    is_read_operation,
    ENTITY_STRATEGIES,
    INVALIDATION_MAP,
)
from dolibarr_mcp.cache.dragonfly import DragonflyCache


class TestCacheStrategies:
    """Test cache strategy configuration."""

    def test_cache_strategy_values(self):
        """Test cache strategy TTL values."""
        assert CacheStrategy.NO_CACHE.value == 0
        assert CacheStrategy.SHORT.value == 30
        assert CacheStrategy.MEDIUM.value == 300
        assert CacheStrategy.LONG.value == 900
        assert CacheStrategy.STATIC.value == 3600

    def test_get_ttl_for_entity_read_ops(self):
        """Test TTL for read operations."""
        # Products have LONG cache
        assert get_ttl_for_entity("get_products") == 900
        assert get_ttl_for_entity("get_product_by_id") == 900

        # Customers have MEDIUM cache
        assert get_ttl_for_entity("get_customers") == 300

        # Invoices have SHORT cache
        assert get_ttl_for_entity("get_invoices") == 30

    def test_get_ttl_for_entity_write_ops(self):
        """Test TTL for write operations (should be 0)."""
        assert get_ttl_for_entity("create_customer") == 0
        assert get_ttl_for_entity("update_product") == 0
        assert get_ttl_for_entity("delete_invoice") == 0

    def test_should_cache_read_ops(self):
        """Test should_cache for read operations."""
        assert should_cache("get_customers") is True
        assert should_cache("get_products") is True
        assert should_cache("search_customers") is True

    def test_should_cache_write_ops(self):
        """Test should_cache for write operations."""
        assert should_cache("create_customer") is False
        assert should_cache("update_product") is False
        assert should_cache("delete_invoice") is False

    def test_should_cache_unknown_tool(self):
        """Test should_cache for unknown tools."""
        assert should_cache("unknown_tool") is False
        assert get_ttl_for_entity("unknown_tool") == 0

    def test_invalidation_targets_customer(self):
        """Test invalidation targets for customer mutations."""
        targets = get_invalidation_targets("create_customer")
        assert "get_customers" in targets
        assert "search_customers" in targets

        targets = get_invalidation_targets("update_customer")
        assert "get_customer_by_id" in targets

    def test_invalidation_targets_product(self):
        """Test invalidation targets for product mutations."""
        targets = get_invalidation_targets("update_product")
        assert "get_products" in targets
        assert "get_product_by_id" in targets
        assert "search_products_by_ref" in targets
        assert "resolve_product_ref" in targets

    def test_invalidation_targets_no_invalidation(self):
        """Test that read operations don't invalidate cache."""
        targets = get_invalidation_targets("get_customers")
        assert targets == []

    def test_is_read_operation(self):
        """Test read operation detection."""
        assert is_read_operation("get_customers") is True
        assert is_read_operation("search_products") is True
        assert is_read_operation("resolve_product_ref") is True

        assert is_read_operation("create_customer") is False
        assert is_read_operation("update_product") is False
        assert is_read_operation("delete_invoice") is False
        assert is_read_operation("add_invoice_line") is False
        assert is_read_operation("validate_invoice") is False


class TestDragonflyCache:
    """Test DragonflyCache client."""

    def test_cache_disabled_by_default_without_redis(self):
        """Test cache is disabled when redis not available."""
        cache = DragonflyCache(enabled=False)
        assert cache.enabled is False
        assert cache._connected is False

    def test_make_key_prefixing(self):
        """Test key prefixing."""
        cache = DragonflyCache(prefix="test:")
        key = cache._make_key("mykey")
        assert key == "test:mykey"

    def test_make_tool_key(self):
        """Test tool key generation."""
        cache = DragonflyCache()

        key1 = cache.make_tool_key("get_customers", {"limit": 100})
        key2 = cache.make_tool_key("get_customers", {"limit": 100})
        key3 = cache.make_tool_key("get_customers", {"limit": 50})

        # Same args should produce same key
        assert key1 == key2
        # Different args should produce different key
        assert key1 != key3
        # Key format
        assert key1.startswith("tool:get_customers:")

    def test_hash_args_consistent(self):
        """Test that arg hashing is consistent."""
        cache = DragonflyCache()

        # Order should not matter
        hash1 = cache._hash_args({"a": 1, "b": 2})
        hash2 = cache._hash_args({"b": 2, "a": 1})
        assert hash1 == hash2

    def test_get_stats_initial(self):
        """Test initial cache statistics."""
        cache = DragonflyCache(enabled=False)
        stats = cache.get_stats()

        assert stats["connected"] is False
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["errors"] == 0
        assert stats["hit_rate"] == "0.0%"

    @pytest.mark.asyncio
    async def test_get_returns_none_when_disconnected(self):
        """Test that get returns None when not connected."""
        cache = DragonflyCache(enabled=False)
        result = await cache.get("any_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_returns_false_when_disconnected(self):
        """Test that set returns False when not connected."""
        cache = DragonflyCache(enabled=False)
        result = await cache.set("key", {"data": "value"})
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_disconnected(self):
        """Test that delete returns False when not connected."""
        cache = DragonflyCache(enabled=False)
        result = await cache.delete("key")
        assert result is False

    @pytest.mark.asyncio
    async def test_invalidate_pattern_returns_zero_when_disconnected(self):
        """Test that invalidate_pattern returns 0 when not connected."""
        cache = DragonflyCache(enabled=False)
        result = await cache.invalidate_pattern("tool:*")
        assert result == 0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with DragonflyCache(enabled=False) as cache:
            assert cache._connected is False

    @pytest.mark.asyncio
    async def test_connect_fails_gracefully_without_server(self):
        """Test that connect fails gracefully."""
        cache = DragonflyCache(host="nonexistent", port=9999)
        # If redis is not installed, enabled will be False
        if cache.enabled:
            result = await cache.connect()
            assert result is False
            assert cache._connected is False


class TestCacheIntegration:
    """Test cache integration with entity strategies."""

    def test_all_read_tools_have_strategies(self):
        """Test that all read tools have cache strategies defined."""
        read_tools = [
            "get_products", "get_product_by_id",
            "get_customers", "get_customer_by_id",
            "get_invoices", "get_invoice_by_id",
            "get_orders", "get_order_by_id",
            "get_proposals", "get_proposal_by_id",
            "get_projects", "get_project_by_id",
            "get_contacts", "get_contact_by_id",
            "get_users", "get_user_by_id",
        ]

        for tool in read_tools:
            assert tool in ENTITY_STRATEGIES, f"Missing strategy for {tool}"
            assert should_cache(tool), f"{tool} should be cacheable"

    def test_all_write_tools_no_cache(self):
        """Test that all write tools have NO_CACHE strategy."""
        write_tools = [
            "create_customer", "update_customer", "delete_customer",
            "create_product", "update_product", "delete_product",
            "create_invoice", "update_invoice", "delete_invoice",
            "create_order", "update_order", "delete_order",
        ]

        for tool in write_tools:
            assert tool in ENTITY_STRATEGIES, f"Missing strategy for {tool}"
            assert not should_cache(tool), f"{tool} should not be cacheable"

    def test_mutation_tools_have_invalidation_targets(self):
        """Test that mutation tools have invalidation targets."""
        mutation_tools = [
            "create_customer", "update_customer", "delete_customer",
            "create_product", "update_product", "delete_product",
            "create_invoice", "update_invoice", "delete_invoice",
        ]

        for tool in mutation_tools:
            targets = get_invalidation_targets(tool)
            assert len(targets) > 0, f"{tool} should have invalidation targets"
