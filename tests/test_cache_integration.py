"""Integration tests for cache with MCP handlers.

These tests verify the cache behavior with real Redis/DragonflyDB
and mocked Dolibarr API responses.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from dolibarr_mcp.cache.dragonfly import DragonflyCache
from dolibarr_mcp.cache.strategies import (
    get_ttl_for_entity,
    get_invalidation_targets,
    should_cache,
)
from dolibarr_mcp.server.handlers import dispatch_tool_cached
from dolibarr_mcp.formats.toon_encoder import encode_response


@pytest_asyncio.fixture
async def cache():
    """Create a test cache instance."""
    cache = DragonflyCache(
        host="localhost",
        port=6379,
        prefix="test_dolibarr:",
        enabled=True
    )
    connected = await cache.connect()
    if not connected:
        pytest.skip("Redis/DragonflyDB not available")

    # Clean test keys before each test
    await cache.invalidate_pattern("*")

    yield cache

    # Cleanup
    await cache.invalidate_pattern("*")
    await cache.disconnect()


@pytest.fixture
def mock_client():
    """Create a mock Dolibarr client."""
    client = MagicMock()

    # Mock customer methods
    client.get_customers = AsyncMock(return_value=[
        {"id": "1", "name": "Customer A", "status": "1"},
        {"id": "2", "name": "Customer B", "status": "1"},
    ])
    client.create_customer = AsyncMock(return_value=999)
    client.delete_customer = AsyncMock(return_value=True)

    # Mock product methods
    client.get_products = AsyncMock(return_value=[
        {"id": "1", "ref": "PROD001", "label": "Product A", "price": "10.00"},
        {"id": "2", "ref": "PROD002", "label": "Product B", "price": "20.00"},
    ])
    client.create_product = AsyncMock(return_value=888)

    return client


class TestCacheIntegration:
    """Test cache integration with MCP handlers."""

    @pytest.mark.asyncio
    async def test_cache_miss_then_hit(self, cache, mock_client):
        """Test that first call is MISS, second call is HIT."""
        # First call - should be MISS
        response1 = await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        assert response1["success"] is True
        stats1 = cache.get_stats()
        assert stats1["misses"] == 1
        assert stats1["hits"] == 0

        # Second call - should be HIT
        response2 = await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        assert response2["success"] is True
        stats2 = cache.get_stats()
        assert stats2["hits"] == 1

        # Client should only be called once
        assert mock_client.get_customers.call_count == 1

    @pytest.mark.asyncio
    async def test_different_args_different_cache_keys(self, cache, mock_client):
        """Test that different args create different cache keys."""
        # Call with limit=10
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        # Call with limit=20 - should be MISS
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 20}, cache
        )

        stats = cache.get_stats()
        assert stats["misses"] == 2
        assert mock_client.get_customers.call_count == 2

    @pytest.mark.asyncio
    async def test_create_invalidates_list_cache(self, cache, mock_client):
        """Test that create operation invalidates list cache."""
        # First, cache the customer list
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        stats1 = cache.get_stats()
        initial_misses = stats1["misses"]

        # Create a customer - should invalidate get_customers cache
        await dispatch_tool_cached(
            mock_client, "create_customer", {"name": "New Customer"}, cache
        )

        # Now get_customers should be MISS again
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        stats2 = cache.get_stats()
        # Should have one more miss because cache was invalidated
        assert stats2["misses"] == initial_misses + 1
        assert mock_client.get_customers.call_count == 2

    @pytest.mark.asyncio
    async def test_write_operations_not_cached(self, cache, mock_client):
        """Test that write operations are not cached."""
        # Create should not be cached
        assert should_cache("create_customer") is False
        assert should_cache("update_customer") is False
        assert should_cache("delete_customer") is False

        # Call create twice
        await dispatch_tool_cached(
            mock_client, "create_customer", {"name": "Test 1"}, cache
        )
        await dispatch_tool_cached(
            mock_client, "create_customer", {"name": "Test 2"}, cache
        )

        # Both calls should hit the API
        assert mock_client.create_customer.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_ttl_varies_by_entity(self, cache, mock_client):
        """Test that different entities have different TTLs."""
        # Products have LONG TTL (900s)
        assert get_ttl_for_entity("get_products") == 900

        # Customers have MEDIUM TTL (300s)
        assert get_ttl_for_entity("get_customers") == 300

        # Invoices have SHORT TTL (30s)
        assert get_ttl_for_entity("get_invoices") == 30

    @pytest.mark.asyncio
    async def test_invalidation_targets_correct(self, cache, mock_client):
        """Test that mutation operations have correct invalidation targets."""
        # create_customer should invalidate get_customers and search_customers
        targets = get_invalidation_targets("create_customer")
        assert "get_customers" in targets
        assert "search_customers" in targets

        # update_customer should also invalidate get_customer_by_id
        targets = get_invalidation_targets("update_customer")
        assert "get_customer_by_id" in targets

    @pytest.mark.asyncio
    async def test_cache_stats_tracking(self, cache, mock_client):
        """Test that cache statistics are tracked correctly."""
        # Initial stats
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Miss
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        # Hit
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        # Hit
        await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == "66.7%"


class TestToonFormatWithCache:
    """Test TOON format output with cached responses."""

    @pytest.mark.asyncio
    async def test_cached_response_toon_format(self, cache, mock_client):
        """Test that cached responses can be formatted as TOON."""
        response = await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        toon = encode_response(response)

        assert "success: true" in toon
        assert "data:" in toon
        # Tabular format for uniform list
        assert "[2]{" in toon  # 2 customers

    @pytest.mark.asyncio
    async def test_error_response_toon_format(self, cache, mock_client):
        """Test that error responses are formatted correctly."""
        # Make client raise an error
        mock_client.get_customers = AsyncMock(side_effect=Exception("API Error"))

        # The dispatch should raise an exception (not handled in current implementation)
        # In production, this would be caught and converted to an error response
        with pytest.raises(Exception, match="API Error"):
            await dispatch_tool_cached(
                mock_client, "get_customers", {"limit": 10}, cache
            )


class TestCacheGracefulDegradation:
    """Test cache behavior when unavailable."""

    @pytest.mark.asyncio
    async def test_disabled_cache_still_works(self, mock_client):
        """Test that MCP works when cache is disabled."""
        cache = DragonflyCache(enabled=False)

        response = await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        assert response["success"] is True
        assert len(response["data"]) == 2

    @pytest.mark.asyncio
    async def test_disconnected_cache_still_works(self, mock_client):
        """Test that MCP works when cache connection fails."""
        cache = DragonflyCache(
            host="nonexistent",
            port=9999,
            enabled=True
        )
        # Don't connect - simulates connection failure

        response = await dispatch_tool_cached(
            mock_client, "get_customers", {"limit": 10}, cache
        )

        assert response["success"] is True
        # All calls should hit the API
        assert mock_client.get_customers.call_count == 1
