"""Plans resource — manage pricing plans for a resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Plan

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class PlansResource:
    """Synchronous plan management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self, resource_id: str) -> list[Plan]:
        """
        List all pricing plans for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            List of Plan objects.
        """
        data = self._http.get(f"/resources/{resource_id}/plans")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Plan.model_validate(item) for item in items]

    def create(
        self,
        resource_id: str,
        name: str,
        price_usdc: float,
        duration_seconds: int,
        *,
        active: bool = True,
    ) -> Plan:
        """
        Create a new pricing plan for a resource.

        Args:
            resource_id: The resource UUID.
            name: Human-readable plan name (e.g., "Monthly", "Annual").
            price_usdc: Plan price in USD.
            duration_seconds: How long access lasts after payment.
            active: Whether this plan is immediately available for purchase.

        Returns:
            The created Plan.
        """
        body = {
            "name": name,
            "price_usdc": price_usdc,
            "duration_seconds": duration_seconds,
            "active": active,
        }
        data = self._http.post(f"/resources/{resource_id}/plans", json=body)
        return Plan.model_validate(data)


class AsyncPlansResource:
    """Asynchronous plan management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self, resource_id: str) -> list[Plan]:
        """
        List all pricing plans for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            List of Plan objects.
        """
        data = await self._http.get(f"/resources/{resource_id}/plans")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Plan.model_validate(item) for item in items]

    async def create(
        self,
        resource_id: str,
        name: str,
        price_usdc: float,
        duration_seconds: int,
        *,
        active: bool = True,
    ) -> Plan:
        """
        Create a new pricing plan for a resource.

        Args:
            resource_id: The resource UUID.
            name: Human-readable plan name.
            price_usdc: Plan price in USD.
            duration_seconds: How long access lasts after payment.
            active: Whether this plan is immediately available.

        Returns:
            The created Plan.
        """
        body = {
            "name": name,
            "price_usdc": price_usdc,
            "duration_seconds": duration_seconds,
            "active": active,
        }
        data = await self._http.post(f"/resources/{resource_id}/plans", json=body)
        return Plan.model_validate(data)
