"""Custom exceptions for Dolibarr API client.

Provides structured error handling with:
- Error codes for programmatic handling
- Retriable flags for AI agent retry logic
- Detailed context for debugging
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


# =============================================================================
# ERROR CODE DEFINITIONS
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
}


def _now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _generate_correlation_id() -> str:
    """Generate a unique correlation ID for error tracking."""
    return str(uuid4())


# =============================================================================
# EXCEPTION CLASSES
# =============================================================================

class DolibarrAPIError(Exception):
    """Base exception for Dolibarr API errors.

    Attributes:
        message: Human-readable error description
        status_code: HTTP status code (e.g., 404, 500)
        code: Error code from ERROR_CODES (e.g., "NOT_FOUND")
        retriable: Whether the operation can be retried
        response_data: Raw response data from API
        correlation_id: Unique ID for error tracking
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
        retriable: Optional[bool] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code or 500
        self.response_data = response_data
        self.correlation_id = correlation_id or _generate_correlation_id()
        self.details = details or {}

        # Determine code and retriable from status if not provided
        if code:
            self.code = code
            default_status, default_retriable = ERROR_CODES.get(code, (500, True))
            self.retriable = retriable if retriable is not None else default_retriable
        else:
            # Infer code from status
            self.code = self._infer_code_from_status(self.status_code)
            _, default_retriable = ERROR_CODES.get(self.code, (500, True))
            self.retriable = retriable if retriable is not None else default_retriable

        super().__init__(self.message)

    @staticmethod
    def _infer_code_from_status(status: int) -> str:
        """Infer error code from HTTP status."""
        status_to_code = {
            400: "VALIDATION_ERROR",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            429: "RATE_LIMITED",
            500: "SERVER_ERROR",
            502: "SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
            504: "TIMEOUT",
        }
        return status_to_code.get(status, "SERVER_ERROR")

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to structured error response.

        Returns:
            Dict with success=False and error details suitable for API response.
        """
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "status": self.status_code,
                "retriable": self.retriable,
                "correlation_id": self.correlation_id,
                "details": self.details,
                "timestamp": _now_iso(),
            }
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message} (status={self.status_code}, retriable={self.retriable})"

    def __repr__(self) -> str:
        return (
            f"DolibarrAPIError(message={self.message!r}, status_code={self.status_code}, "
            f"code={self.code!r}, retriable={self.retriable})"
        )


class DolibarrValidationError(DolibarrAPIError):
    """Exception for validation failures before API calls.

    Used when input parameters fail client-side validation.

    Attributes:
        missing_fields: List of required fields that are missing
        invalid_fields: List of fields with invalid values
        endpoint: The API endpoint that was being called
    """

    def __init__(
        self,
        message: str,
        missing_fields: Optional[List[str]] = None,
        invalid_fields: Optional[List[Dict[str, str]]] = None,
        endpoint: Optional[str] = None,
        status_code: int = 400,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        self.missing_fields = missing_fields or []
        self.invalid_fields = invalid_fields or []
        self.endpoint = endpoint

        # Build details
        details: Dict[str, Any] = {}
        if self.missing_fields:
            details["missing_fields"] = self.missing_fields
        if self.invalid_fields:
            details["invalid_fields"] = self.invalid_fields
        if self.endpoint:
            details["endpoint"] = f"/{endpoint.lstrip('/')}"

        super().__init__(
            message=message,
            status_code=status_code,
            code="VALIDATION_ERROR",
            response_data=response_data,
            retriable=False,
            details=details,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to structured error response with validation details."""
        result = super().to_dict()
        # Add validation-specific fields for easier parsing
        result["error"]["missing_fields"] = self.missing_fields
        result["error"]["invalid_fields"] = self.invalid_fields
        if self.endpoint:
            result["error"]["endpoint"] = self.endpoint
        return result


class DolibarrNotFoundError(DolibarrAPIError):
    """Exception for 404 Not Found errors."""

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id

        super().__init__(
            message=message or f"{entity_type.capitalize()} with ID {entity_id} not found",
            status_code=404,
            code="NOT_FOUND",
            retriable=False,
            details={"entity_type": entity_type, "entity_id": entity_id},
        )


class DolibarrConflictError(DolibarrAPIError):
    """Exception for 409 Conflict errors (e.g., duplicate entries)."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        constraint: Optional[str] = None,
    ):
        details: Dict[str, Any] = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if constraint:
            details["constraint"] = constraint

        super().__init__(
            message=message,
            status_code=409,
            code="CONFLICT",
            retriable=False,
            details=details,
        )


class DolibarrConnectionError(DolibarrAPIError):
    """Exception for connection failures."""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        details: Dict[str, Any] = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__

        super().__init__(
            message=message,
            status_code=503,
            code="CONNECTION_ERROR",
            retriable=True,
            details=details,
        )


class DolibarrTimeoutError(DolibarrAPIError):
    """Exception for request timeout errors."""

    def __init__(
        self,
        message: str = "Request timed out",
        endpoint: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        details: Dict[str, Any] = {}
        if endpoint:
            details["endpoint"] = endpoint
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds

        super().__init__(
            message=message,
            status_code=504,
            code="TIMEOUT",
            retriable=True,
            details=details,
        )


class DolibarrRateLimitError(DolibarrAPIError):
    """Exception for rate limiting (429) errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        details: Dict[str, Any] = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            status_code=429,
            code="RATE_LIMITED",
            retriable=True,
            details=details,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_validation_error(
    endpoint: str,
    missing_fields: Optional[List[str]] = None,
    invalid_fields: Optional[List[Dict[str, str]]] = None,
    message: str = "Validation failed",
) -> DolibarrValidationError:
    """Build a validation error with structured details.

    Args:
        endpoint: API endpoint being called
        missing_fields: List of required fields that are missing
        invalid_fields: List of dicts with field/message for invalid values
        message: Error message

    Returns:
        DolibarrValidationError instance
    """
    # Build detailed message
    details_parts: List[str] = []
    if missing_fields:
        details_parts.append(f"missing: {', '.join(missing_fields)}")
    if invalid_fields:
        details_parts.append(
            "invalid: " + ", ".join(f["field"] for f in (invalid_fields or []))
        )

    if details_parts:
        message = f"{message} ({'; '.join(details_parts)})"

    return DolibarrValidationError(
        message=message,
        missing_fields=missing_fields,
        invalid_fields=invalid_fields,
        endpoint=endpoint,
    )


def build_internal_error(
    endpoint: str,
    message: str,
    correlation_id: Optional[str] = None,
) -> DolibarrAPIError:
    """Build an internal server error with correlation ID.

    Args:
        endpoint: API endpoint where error occurred
        message: Error message
        correlation_id: Optional correlation ID (auto-generated if not provided)

    Returns:
        DolibarrAPIError instance
    """
    return DolibarrAPIError(
        message=message,
        status_code=500,
        code="SERVER_ERROR",
        retriable=True,
        correlation_id=correlation_id,
        details={"endpoint": f"/{endpoint.lstrip('/')}"},
    )
