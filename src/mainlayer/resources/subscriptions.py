"""Subscriptions resource — manage recurring access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import Subscription

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class SubscriptionsResource:
    """Synchronous subscription management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self) -> list[Subscription]:
        """
        List all subscriptions for the authenticated account.

        Returns:
            List of Subscription objects.
        """
        data = self._http.get("/subscriptions")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Subscription.model_validate(item) for item in items]

    def create(self, **kwargs: Any) -> Subscription:
        """
        Create a new subscription.

        Args:
            **kwargs: Subscription fields as accepted by the API.

        Returns:
            The created Subscription.
        """
        data = self._http.post("/subscriptions", json=kwargs)
        return Subscription.model_validate(data)

    def cancel(self, subscription_id: str) -> None:
        """
        Cancel (delete) a subscription.

        Args:
            subscription_id: The subscription UUID to cancel.
        """
        self._http.delete(f"/subscriptions/{subscription_id}")


class AsyncSubscriptionsResource:
    """Asynchronous subscription management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self) -> list[Subscription]:
        """
        List all subscriptions for the authenticated account.

        Returns:
            List of Subscription objects.
        """
        data = await self._http.get("/subscriptions")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Subscription.model_validate(item) for item in items]

    async def create(self, **kwargs: Any) -> Subscription:
        """
        Create a new subscription.

        Args:
            **kwargs: Subscription fields as accepted by the API.

        Returns:
            The created Subscription.
        """
        data = await self._http.post("/subscriptions", json=kwargs)
        return Subscription.model_validate(data)

    async def cancel(self, subscription_id: str) -> None:
        """
        Cancel (delete) a subscription.

        Args:
            subscription_id: The subscription UUID to cancel.
        """
        await self._http.delete(f"/subscriptions/{subscription_id}")
