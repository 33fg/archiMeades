"""Custom exception hierarchy with RFC 7807 Problem Details support."""

from typing import Any


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class ResourceNotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found", detail: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=404, detail=detail)


class ValidationError(AppException):
    """Validation error (422)."""

    def __init__(self, message: str = "Validation error", detail: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=422, detail=detail)


class UnauthorizedError(AppException):
    """Authentication required (401)."""

    def __init__(self, message: str = "Authentication required", detail: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=401, detail=detail)


class ForbiddenError(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "Insufficient permissions", detail: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=403, detail=detail)


class ConflictError(AppException):
    """Resource conflict (409)."""

    def __init__(self, message: str = "Resource conflict", detail: dict[str, Any] | None = None) -> None:
        super().__init__(message, status_code=409, detail=detail)
