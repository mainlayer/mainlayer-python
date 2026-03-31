"""Resources — create and manage vendored assets and API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import FeeModel, Resource, ResourceType

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


def _build_resource_body(
    slug: str,
    type: ResourceType | str,
    price_usdc: float,
    fee_model: FeeModel | str,
    description: str | None = None,
    callback_url: str | None = None,
    credits_per_payment: int | None = None,
    duration_seconds: int | None = None,
    quota_calls: int | None = None,
    discoverable: bool | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "slug": slug,
        "type": type if isinstance(type, str) else type.value,
        "price_usdc": price_usdc,
        "fee_model": fee_model if isinstance(fee_model, str) else fee_model.value,
    }
    if description is not None:
        body["description"] = description
    if callback_url is not None:
        body["callback_url"] = callback_url
    if credits_per_payment is not None:
        body["credits_per_payment"] = credits_per_payment
    if duration_seconds is not None:
        body["duration_seconds"] = duration_seconds
    if quota_calls is not None:
        body["quota_calls"] = quota_calls
    if discoverable is not None:
        body["discoverable"] = discoverable
    return body


class ResourcesResource:
    """Synchronous resource management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def create(
        self,
        slug: str,
        type: ResourceType | str,
        price_usdc: float,
        fee_model: FeeModel | str = FeeModel.pay_per_call,
        *,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        discoverable: bool | None = None,
    ) -> Resource:
        """
        Create a new resource (what you sell to buyers).

        Args:
            slug: URL-friendly identifier (e.g., "my-ai-tool"). Must be unique per vendor.
            type: Resource type — "api", "file", "endpoint", or "page".
            price_usdc: Price in USD (e.g., ``0.10`` for 10 cents).
            fee_model: Billing model — "one_time", "subscription", or "pay_per_call".
            description: Optional human-readable description shown in discovery.
            callback_url: Optional URL called when a payment succeeds.
            credits_per_payment: For pay_per_call — credits granted per payment.
            duration_seconds: For subscription — access duration in seconds.
            quota_calls: Optional call quota per entitlement period.
            discoverable: Whether this resource appears in public discovery.

        Returns:
            The created Resource.
        """
        body = _build_resource_body(
            slug, type, price_usdc, fee_model,
            description=description,
            callback_url=callback_url,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            quota_calls=quota_calls,
            discoverable=discoverable,
        )
        data = self._http.post("/resources", json=body)
        return Resource.model_validate(data)

    def list(self) -> list[Resource]:
        """
        List all resources owned by the authenticated vendor.

        Returns:
            List of Resource objects.
        """
        data = self._http.get("/resources")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Resource.model_validate(item) for item in items]

    def get(self, resource_id: str) -> Resource:
        """
        Retrieve a specific resource by ID.

        Args:
            resource_id: The resource UUID.

        Returns:
            The Resource.
        """
        data = self._http.get(f"/resources/{resource_id}")
        return Resource.model_validate(data)

    def get_public(self, resource_id: str) -> Resource:
        """
        Retrieve public information about a resource. Does not require authentication.

        Args:
            resource_id: The resource UUID.

        Returns:
            Public Resource data.
        """
        data = self._http.get(f"/resources/public/{resource_id}")
        return Resource.model_validate(data)

    def update(
        self,
        resource_id: str,
        *,
        slug: str | None = None,
        type: ResourceType | str | None = None,
        price_usdc: float | None = None,
        fee_model: FeeModel | str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        discoverable: bool | None = None,
        active: bool | None = None,
    ) -> Resource:
        """
        Update a resource. Only provided fields are changed.

        Args:
            resource_id: The resource UUID to update.
            slug: New slug.
            type: New resource type.
            price_usdc: New price in USD.
            fee_model: New fee model.
            description: New description.
            callback_url: New callback URL.
            credits_per_payment: New credits per payment.
            duration_seconds: New duration in seconds.
            quota_calls: New quota calls.
            discoverable: New discoverable flag.
            active: Whether the resource is active.

        Returns:
            The updated Resource.
        """
        body: dict[str, Any] = {}
        if slug is not None:
            body["slug"] = slug
        if type is not None:
            body["type"] = type if isinstance(type, str) else type.value
        if price_usdc is not None:
            body["price_usdc"] = price_usdc
        if fee_model is not None:
            body["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        if description is not None:
            body["description"] = description
        if callback_url is not None:
            body["callback_url"] = callback_url
        if credits_per_payment is not None:
            body["credits_per_payment"] = credits_per_payment
        if duration_seconds is not None:
            body["duration_seconds"] = duration_seconds
        if quota_calls is not None:
            body["quota_calls"] = quota_calls
        if discoverable is not None:
            body["discoverable"] = discoverable
        if active is not None:
            body["active"] = active
        data = self._http.patch(f"/resources/{resource_id}", json=body)
        return Resource.model_validate(data)

    def delete(self, resource_id: str) -> None:
        """
        Delete a resource.

        Args:
            resource_id: The resource UUID to delete.
        """
        self._http.delete(f"/resources/{resource_id}")


class AsyncResourcesResource:
    """Asynchronous resource management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def create(
        self,
        slug: str,
        type: ResourceType | str,
        price_usdc: float,
        fee_model: FeeModel | str = FeeModel.pay_per_call,
        *,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        discoverable: bool | None = None,
    ) -> Resource:
        """
        Create a new resource.

        Args:
            slug: URL-friendly identifier for the resource.
            type: Resource type — "api", "file", "endpoint", or "page".
            price_usdc: Price in USD (e.g., ``0.10`` for 10 cents).
            fee_model: Billing model — "one_time", "subscription", or "pay_per_call".
            description: Optional description shown in discovery.
            callback_url: Optional URL called on successful payment.
            credits_per_payment: Credits granted per payment (pay_per_call).
            duration_seconds: Access duration in seconds (subscription).
            quota_calls: Call quota per entitlement period.
            discoverable: Whether visible in public discovery.

        Returns:
            The created Resource.
        """
        body = _build_resource_body(
            slug, type, price_usdc, fee_model,
            description=description,
            callback_url=callback_url,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            quota_calls=quota_calls,
            discoverable=discoverable,
        )
        data = await self._http.post("/resources", json=body)
        return Resource.model_validate(data)

    async def list(self) -> list[Resource]:
        """List all resources owned by the authenticated vendor."""
        data = await self._http.get("/resources")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Resource.model_validate(item) for item in items]

    async def get(self, resource_id: str) -> Resource:
        """Retrieve a specific resource by ID."""
        data = await self._http.get(f"/resources/{resource_id}")
        return Resource.model_validate(data)

    async def get_public(self, resource_id: str) -> Resource:
        """Retrieve public information about a resource without authentication."""
        data = await self._http.get(f"/resources/public/{resource_id}")
        return Resource.model_validate(data)

    async def update(
        self,
        resource_id: str,
        *,
        slug: str | None = None,
        type: ResourceType | str | None = None,
        price_usdc: float | None = None,
        fee_model: FeeModel | str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        discoverable: bool | None = None,
        active: bool | None = None,
    ) -> Resource:
        """Update a resource. Only provided fields are changed."""
        body: dict[str, Any] = {}
        if slug is not None:
            body["slug"] = slug
        if type is not None:
            body["type"] = type if isinstance(type, str) else type.value
        if price_usdc is not None:
            body["price_usdc"] = price_usdc
        if fee_model is not None:
            body["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        if description is not None:
            body["description"] = description
        if callback_url is not None:
            body["callback_url"] = callback_url
        if credits_per_payment is not None:
            body["credits_per_payment"] = credits_per_payment
        if duration_seconds is not None:
            body["duration_seconds"] = duration_seconds
        if quota_calls is not None:
            body["quota_calls"] = quota_calls
        if discoverable is not None:
            body["discoverable"] = discoverable
        if active is not None:
            body["active"] = active
        data = await self._http.patch(f"/resources/{resource_id}", json=body)
        return Resource.model_validate(data)

    async def delete(self, resource_id: str) -> None:
        """Delete a resource."""
        await self._http.delete(f"/resources/{resource_id}")
