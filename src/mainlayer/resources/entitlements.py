"""Entitlements resource — check and list buyer access."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Entitlement, EntitlementCheck

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class EntitlementsResource:
    """Synchronous entitlement operations."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(
        self,
        *,
        resource_id: str | None = None,
        payer_wallet: str | None = None,
    ) -> list[Entitlement]:
        """
        List entitlements, optionally filtered.

        Args:
            resource_id: Filter by resource UUID.
            payer_wallet: Filter by buyer wallet address.

        Returns:
            List of Entitlement records.
        """
        params: dict = {}
        if resource_id is not None:
            params["resource_id"] = resource_id
        if payer_wallet is not None:
            params["payer_wallet"] = payer_wallet
        data = self._http.get("/entitlements", params=params or None)
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Entitlement.model_validate(item) for item in items]

    def check(self, resource_id: str, payer_wallet: str) -> EntitlementCheck:
        """
        Check whether a buyer has active access to a resource.

        Args:
            resource_id: The resource UUID.
            payer_wallet: The buyer's wallet address.

        Returns:
            EntitlementCheck with ``allowed`` boolean and optional details.
        """
        params = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        data = self._http.get("/entitlements/check", params=params)
        return EntitlementCheck.model_validate(data)


class AsyncEntitlementsResource:
    """Asynchronous entitlement operations."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(
        self,
        *,
        resource_id: str | None = None,
        payer_wallet: str | None = None,
    ) -> list[Entitlement]:
        """
        List entitlements, optionally filtered.

        Args:
            resource_id: Filter by resource UUID.
            payer_wallet: Filter by buyer wallet address.

        Returns:
            List of Entitlement records.
        """
        params: dict = {}
        if resource_id is not None:
            params["resource_id"] = resource_id
        if payer_wallet is not None:
            params["payer_wallet"] = payer_wallet
        data = await self._http.get("/entitlements", params=params or None)
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Entitlement.model_validate(item) for item in items]

    async def check(self, resource_id: str, payer_wallet: str) -> EntitlementCheck:
        """
        Check whether a buyer has active access to a resource.

        Args:
            resource_id: The resource UUID.
            payer_wallet: The buyer's wallet address.

        Returns:
            EntitlementCheck with ``allowed`` boolean and optional details.
        """
        params = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        data = await self._http.get("/entitlements/check", params=params)
        return EntitlementCheck.model_validate(data)
