"""API Keys resource — create, list, and delete API keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import ApiKey

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class ApiKeysResource:
    """Synchronous API key management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def create(self, name: str) -> ApiKey:
        """
        Create a new API key.

        The ``key`` field in the response contains the raw secret value — it is
        only returned once and cannot be retrieved again.

        Args:
            name: Human-readable name for the key (e.g., "production", "ci-bot").

        Returns:
            ApiKey with the ``key`` field populated.
        """
        data = self._http.post("/api-keys", json={"name": name})
        return ApiKey.model_validate(data)

    def list(self) -> list[ApiKey]:
        """
        List all API keys for the authenticated account.

        Returns:
            List of ApiKey objects. The ``key`` field is not included.
        """
        data = self._http.get("/api-keys")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [ApiKey.model_validate(item) for item in items]

    def delete(self, key_id: str) -> None:
        """
        Permanently delete an API key.

        Args:
            key_id: The ID of the API key to delete.
        """
        self._http.delete(f"/api-keys/{key_id}")


class AsyncApiKeysResource:
    """Asynchronous API key management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def create(self, name: str) -> ApiKey:
        """
        Create a new API key.

        Args:
            name: Human-readable name for the key.

        Returns:
            ApiKey with the ``key`` field populated (only shown once).
        """
        data = await self._http.post("/api-keys", json={"name": name})
        return ApiKey.model_validate(data)

    async def list(self) -> list[ApiKey]:
        """
        List all API keys for the authenticated account.

        Returns:
            List of ApiKey objects.
        """
        data = await self._http.get("/api-keys")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [ApiKey.model_validate(item) for item in items]

    async def delete(self, key_id: str) -> None:
        """
        Permanently delete an API key.

        Args:
            key_id: The ID of the API key to delete.
        """
        await self._http.delete(f"/api-keys/{key_id}")
