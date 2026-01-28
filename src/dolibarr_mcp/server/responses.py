"""Unified response wrappers for Dolibarr MCP Server.

Provides consistent response formatting for all tool operations,
including success responses, error responses, and paginated results.
"""

from typing import Any, Dict, List, Optional

# =============================================================================
# ERROR CODES - Standard error codes with (status_code, retriable) tuples
# =============================================================================

ERROR_CODES: Dict[str, tuple] = {
    # Client errors - do not retry
    "VALIDATION_ERROR": (400, False),
    "INVALID_PARAMETER": (400, False),
    "MISSING_REQUIRED_FIELD": (400, False),
    "UNAUTHORIZED": (401, False),
    "FORBIDDEN": (403, False),
    "NOT_FOUND": (404, False),
    "CONFLICT": (409, False),
    "DUPLICATE_ENTRY": (409, False),

    # Server errors - may retry
    "RATE_LIMITED": (429, True),
    "SERVER_ERROR": (500, True),
    "SERVICE_UNAVAILABLE": (503, True),
    "TIMEOUT": (504, True),
    "CONNECTION_ERROR": (503, True),

    # Tool-specific errors
    "UNKNOWN_TOOL": (404, False),
    "TOOL_EXECUTION_ERROR": (500, True),
}


def success_response(
    data: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized success response.

    Args:
        data: The response data (any JSON-serializable type)
        metadata: Optional metadata dict (e.g., pagination info, timing)

    Returns:
        Structured response with success=True, data, and metadata

    Example:
        >>> success_response({"id": 1, "name": "Test"})
        {"success": True, "data": {"id": 1, "name": "Test"}, "metadata": {}}

        >>> success_response([1, 2, 3], {"count": 3})
        {"success": True, "data": [1, 2, 3], "metadata": {"count": 3}}
    """
    return {
        "success": True,
        "data": data,
        "metadata": metadata or {}
    }


def error_response(
    code: str,
    message: str,
    status: Optional[int] = None,
    retriable: Optional[bool] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response.

    Args:
        code: Error code from ERROR_CODES (e.g., "VALIDATION_ERROR")
        message: Human-readable error message
        status: HTTP status code (auto-derived from code if not provided)
        retriable: Whether the operation can be retried (auto-derived if not provided)
        details: Additional error context (field names, constraints, etc.)

    Returns:
        Structured error response with success=False and error details

    Example:
        >>> error_response("NOT_FOUND", "Customer with ID 123 not found")
        {
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Customer with ID 123 not found",
                "status": 404,
                "retriable": False,
                "details": {}
            }
        }

        >>> error_response(
        ...     "VALIDATION_ERROR",
        ...     "Email already exists",
        ...     details={"field": "email", "constraint": "unique"}
        ... )
        {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Email already exists",
                "status": 400,
                "retriable": False,
                "details": {"field": "email", "constraint": "unique"}
            }
        }
    """
    # Get defaults from ERROR_CODES if not explicitly provided
    default_status, default_retriable = ERROR_CODES.get(code, (500, True))

    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "status": status if status is not None else default_status,
            "retriable": retriable if retriable is not None else default_retriable,
            "details": details or {}
        }
    }


def paginated_response(
    data: List[Any],
    limit: int,
    offset: int,
    total: Optional[int] = None
) -> Dict[str, Any]:
    """Create a standardized paginated response.

    Args:
        data: List of items for this page
        limit: Maximum items requested per page
        offset: Starting offset (0-indexed)
        total: Total count of items (if known). If None, has_more is based on data length.

    Returns:
        Success response with pagination metadata

    Example:
        >>> paginated_response([{"id": 1}, {"id": 2}], limit=10, offset=0, total=100)
        {
            "success": True,
            "data": [{"id": 1}, {"id": 2}],
            "metadata": {
                "pagination": {
                    "limit": 10,
                    "offset": 0,
                    "total": 100,
                    "count": 2,
                    "has_more": True
                }
            }
        }
    """
    count = len(data)

    # Determine has_more based on total or data length
    if total is not None:
        has_more = offset + count < total
    else:
        # If total unknown, assume more if we got a full page
        has_more = count >= limit
        total = None  # Explicitly set to None for response

    return success_response(
        data=data,
        metadata={
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "count": count,
                "has_more": has_more
            }
        }
    )


def list_response(
    data: List[Any],
    limit: int,
    total: Optional[int] = None
) -> Dict[str, Any]:
    """Convenience wrapper for list responses with offset=0.

    Args:
        data: List of items
        limit: Maximum items requested
        total: Total count if known

    Returns:
        Paginated response with offset=0
    """
    return paginated_response(data, limit, offset=0, total=total)


def created_response(
    entity_id: Any,
    entity_type: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized response for entity creation.

    Args:
        entity_id: The ID of the created entity
        entity_type: Type of entity (e.g., "customer", "invoice")
        additional_data: Any additional data to include

    Returns:
        Success response with created entity ID

    Example:
        >>> created_response(123, "customer")
        {
            "success": True,
            "data": {"id": 123, "type": "customer"},
            "metadata": {"action": "created"}
        }
    """
    data = {"id": entity_id, "type": entity_type}
    if additional_data:
        data.update(additional_data)

    return success_response(
        data=data,
        metadata={"action": "created"}
    )


def deleted_response(
    entity_id: Any,
    entity_type: str
) -> Dict[str, Any]:
    """Create a standardized response for entity deletion.

    Args:
        entity_id: The ID of the deleted entity
        entity_type: Type of entity (e.g., "customer", "invoice")

    Returns:
        Success response confirming deletion
    """
    return success_response(
        data={"id": entity_id, "type": entity_type, "deleted": True},
        metadata={"action": "deleted"}
    )


def updated_response(
    entity_id: Any,
    entity_type: str,
    updated_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized response for entity updates.

    Args:
        entity_id: The ID of the updated entity
        entity_type: Type of entity
        updated_data: The updated entity data (if available)

    Returns:
        Success response confirming update
    """
    data = {"id": entity_id, "type": entity_type}
    if updated_data:
        data["updated"] = updated_data

    return success_response(
        data=data,
        metadata={"action": "updated"}
    )
