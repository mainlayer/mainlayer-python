"""
Exception types for the Mainlayer SDK.
"""

from __future__ import annotations


class MainlayerError(Exception):
    """
    Raised when the Mainlayer API returns an error or a request fails.

    Attributes:
        message: Human-readable description of the error.
        status_code: HTTP status code (0 for network/transport errors).
        code: Machine-readable error code from the API (e.g., "resource_not_found").
    """

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

    def __repr__(self) -> str:
        return (
            f"MainlayerError(message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"code={self.code!r})"
        )


class AuthenticationError(MainlayerError):
    """Raised for 401 Unauthorized responses."""


class PermissionError(MainlayerError):
    """Raised for 403 Forbidden responses."""


class NotFoundError(MainlayerError):
    """Raised for 404 Not Found responses."""


class ConflictError(MainlayerError):
    """Raised for 409 Conflict responses (e.g., duplicate resource slug)."""


class RateLimitError(MainlayerError):
    """Raised for 429 Too Many Requests responses after all retries are exhausted."""


class ValidationError(MainlayerError):
    """Raised for 422 Unprocessable Entity responses."""
