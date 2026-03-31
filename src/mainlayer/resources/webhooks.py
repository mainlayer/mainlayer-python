"""Webhooks resource — manage event delivery endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Webhook

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class WebhooksResource:
    """Synchronous webhook management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self) -> list[Webhook]:
        """
        List all webhooks for the authenticated account.

        Returns:
            List of Webhook objects.
        """
        data = self._http.get("/webhooks")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Webhook.model_validate(item) for item in items]

    def create(
        self,
        url: str,
        events: list[str],
        *,
        resource_id: str | None = None,
    ) -> Webhook:
        """
        Register a new webhook endpoint.

        Args:
            url: HTTPS URL to receive event notifications. Must use HTTPS.
            events: List of event names to subscribe to (e.g., ["payment.created"]).
            resource_id: Optional resource UUID to scope this webhook.

        Returns:
            The created Webhook.
        """
        body: dict = {"url": url, "events": events}
        if resource_id is not None:
            body["resource_id"] = resource_id
        data = self._http.post("/webhooks", json=body)
        return Webhook.model_validate(data)

    def delete(self, webhook_id: str) -> None:
        """
        Delete a webhook.

        Args:
            webhook_id: The webhook UUID to delete.
        """
        self._http.delete(f"/webhooks/{webhook_id}")


class AsyncWebhooksResource:
    """Asynchronous webhook management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self) -> list[Webhook]:
        """
        List all webhooks for the authenticated account.

        Returns:
            List of Webhook objects.
        """
        data = await self._http.get("/webhooks")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Webhook.model_validate(item) for item in items]

    async def create(
        self,
        url: str,
        events: list[str],
        *,
        resource_id: str | None = None,
    ) -> Webhook:
        """
        Register a new webhook endpoint.

        Args:
            url: HTTPS URL to receive event notifications.
            events: List of event names to subscribe to.
            resource_id: Optional resource UUID to scope this webhook.

        Returns:
            The created Webhook.
        """
        body: dict = {"url": url, "events": events}
        if resource_id is not None:
            body["resource_id"] = resource_id
        data = await self._http.post("/webhooks", json=body)
        return Webhook.model_validate(data)

    async def delete(self, webhook_id: str) -> None:
        """
        Delete a webhook.

        Args:
            webhook_id: The webhook UUID to delete.
        """
        await self._http.delete(f"/webhooks/{webhook_id}")
