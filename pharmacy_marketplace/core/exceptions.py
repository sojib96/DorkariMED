"""
Centralized exception handler for DRF.

Returns a consistent JSON envelope:
{
    "error": {
        "code": "validation_error",
        "message": "Human-readable summary",
        "details": [field-level errors, if any]
    }
}
"""

from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Wrap DRF exceptions into a standard error envelope."""
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data

        # Build consistent envelope
        error_payload = {
            "error": {
                "code": _get_error_code(response.status_code, exc),
                "message": _get_error_message(errors, exc),
                "details": errors if isinstance(errors, dict) else None,
            }
        }

        # For non-field errors that are lists (e.g., multiple non_field_errors)
        if isinstance(errors, list):
            error_payload["error"]["details"] = {"non_field_errors": errors}

        response.data = error_payload

    return response


def _get_error_code(status_code, exc):
    """Map HTTP status codes to machine-readable error codes."""
    code_map = {
        status.HTTP_400_BAD_REQUEST: "validation_error",
        status.HTTP_401_UNAUTHORIZED: "authentication_error",
        status.HTTP_403_FORBIDDEN: "permission_denied",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
        status.HTTP_409_CONFLICT: "conflict",
        status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "server_error",
    }
    return code_map.get(status_code, "error")


def _get_error_message(errors, exc):
    """Extract a human-readable summary from the exception or errors dict."""
    if isinstance(errors, str):
        return errors
    if isinstance(errors, list):
        return "; ".join(str(e) for e in errors[:3])
    if isinstance(errors, dict):
        # Get first message from any field
        first = next(iter(errors.values()), None)
        if isinstance(first, list):
            return str(first[0]) if first else str(exc)
        if isinstance(first, str):
            return first
    return str(exc)
