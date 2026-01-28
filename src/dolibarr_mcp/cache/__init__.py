"""Cache module for Dolibarr MCP with DragonflyDB support."""

from .dragonfly import DragonflyCache, get_cache
from .strategies import CacheStrategy, get_ttl_for_entity

__all__ = [
    "DragonflyCache",
    "get_cache",
    "CacheStrategy",
    "get_ttl_for_entity",
]
