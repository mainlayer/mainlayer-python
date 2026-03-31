"""Resources — create and manage vendored assets and API endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import (
    ActivateResponse,
    FeeModel,
    PaymentRequiredPayload,
    QuotaConfig,
    Resource,
    ResourceType,
    WebhookSecretResponse,
)

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


def _build_resource_body(
    slug: str,
    type: ResourceType | str,
    price_usdc: float,
    fee_model: FeeModel | str,
    vendor_wallet: str | None = None,
    description: str | None = None,
    callback_url: str | None = None,
    credits_per_payment: int | None = None,
    duration_seconds: int | None = None,
    quota_calls: int | None = None,
    overage_price_usdc: float | None = None,
    metadata: dict[str, Any] | None = None,
    discoverable: bool | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "slug": slug,
        "type": type if isinstance(type, str) else type.value,
        "price_usdc": price_usdc,
        "fee_model": fee_model if isinstance(fee_model, str) else fee_model.value,
    }
    if vendor_wallet is not None:
        body["vendor_wallet"] = vendor_wallet
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
    if overage_price_usdc is not None:
        body["overage_price_usdc"] = overage_price_usdc
    if metadata is not None:
        body["metadata"] = metadata
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
        vendor_wallet: str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        overage_price_usdc: float | None = None,
        metadata: dict[str, Any] | None = None,
        discoverable: bool | None = None,
    ) -> Resource:
        """
        Create a new resource (what you sell to buyers).

        Args:
            slug: URL-friendly identifier (e.g., "my-ai-tool"). Must be unique per vendor.
            type: Resource type — "api", "file", "endpoint", or "page".
            price_usdc: Price in USD (e.g., ``0.10`` for 10 cents).
            fee_model: Billing model — "one_time", "subscription", or "pay_per_call".
            vendor_wallet: Wallet address that receives payments for this resource.
            description: Optional human-readable description shown in discovery.
            callback_url: Optional URL called when a payment succeeds.
            credits_per_payment: For pay_per_call — credits granted per payment.
            duration_seconds: For subscription — access duration in seconds.
            quota_calls: Optional call quota per entitlement period.
            overage_price_usdc: Per-call price once the quota is exhausted.
            metadata: Arbitrary key-value metadata stored with the resource.
            discoverable: Whether this resource appears in public discovery.

        Returns:
            The created Resource.
        """
        body = _build_resource_body(
            slug, type, price_usdc, fee_model,
            vendor_wallet=vendor_wallet,
            description=description,
            callback_url=callback_url,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            quota_calls=quota_calls,
            overage_price_usdc=overage_price_usdc,
            metadata=metadata,
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
            Public Resource data including facilitator_url.
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
        vendor_wallet: str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        overage_price_usdc: float | None = None,
        metadata: dict[str, Any] | None = None,
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
            vendor_wallet: New vendor wallet address.
            description: New description.
            callback_url: New callback URL.
            credits_per_payment: New credits per payment.
            duration_seconds: New duration in seconds.
            quota_calls: New quota calls.
            overage_price_usdc: New overage price per call.
            metadata: New metadata dict.
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
        if vendor_wallet is not None:
            body["vendor_wallet"] = vendor_wallet
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
        if overage_price_usdc is not None:
            body["overage_price_usdc"] = overage_price_usdc
        if metadata is not None:
            body["metadata"] = metadata
        if discoverable is not None:
            body["discoverable"] = discoverable
        if active is not None:
            body["active"] = active
        data = self._http.put(f"/resources/{resource_id}", json=body)
        return Resource.model_validate(data)

    def delete(self, resource_id: str) -> None:
        """
        Deactivate a resource.

        Args:
            resource_id: The resource UUID to deactivate.
        """
        self._http.delete(f"/resources/{resource_id}")

    def activate(self, resource_id: str) -> ActivateResponse:
        """
        Activate a resource and make it available for purchase.

        Args:
            resource_id: The resource UUID to activate.

        Returns:
            ActivateResponse with updated active/discoverable status.
        """
        data = self._http.patch(f"/resources/{resource_id}/activate")
        return ActivateResponse.model_validate(data)

    def get_payment_required(self, resource_id: str) -> PaymentRequiredPayload:
        """
        Retrieve the payment-required payload for a resource.

        This returns the data a buyer needs to initiate payment.

        Args:
            resource_id: The resource UUID.

        Returns:
            PaymentRequiredPayload with pricing and payment details.
        """
        data = self._http.get(f"/payment-required/{resource_id}")
        return PaymentRequiredPayload.model_validate(data or {})

    def get_quota(self, resource_id: str) -> QuotaConfig:
        """
        Retrieve the quota configuration for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            QuotaConfig with per-wallet purchase and call limits.
        """
        data = self._http.get(f"/resources/{resource_id}/quota")
        return QuotaConfig.model_validate(data or {})

    def set_quota(
        self,
        resource_id: str,
        *,
        max_purchases_per_wallet: int | None = None,
        max_calls_per_day_per_wallet: int | None = None,
    ) -> QuotaConfig:
        """
        Set or update the quota configuration for a resource.

        Args:
            resource_id: The resource UUID.
            max_purchases_per_wallet: Maximum purchases allowed per unique wallet address.
            max_calls_per_day_per_wallet: Maximum API calls per day per unique wallet.

        Returns:
            Updated QuotaConfig.
        """
        body: dict[str, Any] = {}
        if max_purchases_per_wallet is not None:
            body["max_purchases_per_wallet"] = max_purchases_per_wallet
        if max_calls_per_day_per_wallet is not None:
            body["max_calls_per_day_per_wallet"] = max_calls_per_day_per_wallet
        data = self._http.put(f"/resources/{resource_id}/quota", json=body)
        return QuotaConfig.model_validate(data or {})

    def delete_quota(self, resource_id: str) -> None:
        """
        Remove the quota configuration from a resource.

        Args:
            resource_id: The resource UUID.
        """
        self._http.delete(f"/resources/{resource_id}/quota")

    def get_webhook_secret(self, resource_id: str) -> WebhookSecretResponse:
        """
        Retrieve the HMAC secret used to verify webhook payloads for this resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            WebhookSecretResponse containing the webhook_secret string.
        """
        data = self._http.get(f"/resources/{resource_id}/webhook-secret")
        return WebhookSecretResponse.model_validate(data)


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
        vendor_wallet: str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        overage_price_usdc: float | None = None,
        metadata: dict[str, Any] | None = None,
        discoverable: bool | None = None,
    ) -> Resource:
        """
        Create a new resource.

        Args:
            slug: URL-friendly identifier for the resource.
            type: Resource type — "api", "file", "endpoint", or "page".
            price_usdc: Price in USD (e.g., ``0.10`` for 10 cents).
            fee_model: Billing model — "one_time", "subscription", or "pay_per_call".
            vendor_wallet: Wallet address that receives payments for this resource.
            description: Optional description shown in discovery.
            callback_url: Optional URL called on successful payment.
            credits_per_payment: Credits granted per payment (pay_per_call).
            duration_seconds: Access duration in seconds (subscription).
            quota_calls: Call quota per entitlement period.
            overage_price_usdc: Per-call price once the quota is exhausted.
            metadata: Arbitrary key-value metadata stored with the resource.
            discoverable: Whether visible in public discovery.

        Returns:
            The created Resource.
        """
        body = _build_resource_body(
            slug, type, price_usdc, fee_model,
            vendor_wallet=vendor_wallet,
            description=description,
            callback_url=callback_url,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            quota_calls=quota_calls,
            overage_price_usdc=overage_price_usdc,
            metadata=metadata,
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
        vendor_wallet: str | None = None,
        description: str | None = None,
        callback_url: str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        quota_calls: int | None = None,
        overage_price_usdc: float | None = None,
        metadata: dict[str, Any] | None = None,
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
        if vendor_wallet is not None:
            body["vendor_wallet"] = vendor_wallet
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
        if overage_price_usdc is not None:
            body["overage_price_usdc"] = overage_price_usdc
        if metadata is not None:
            body["metadata"] = metadata
        if discoverable is not None:
            body["discoverable"] = discoverable
        if active is not None:
            body["active"] = active
        data = await self._http.put(f"/resources/{resource_id}", json=body)
        return Resource.model_validate(data)

    async def delete(self, resource_id: str) -> None:
        """Deactivate a resource."""
        await self._http.delete(f"/resources/{resource_id}")

    async def activate(self, resource_id: str) -> ActivateResponse:
        """
        Activate a resource and make it available for purchase.

        Args:
            resource_id: The resource UUID to activate.

        Returns:
            ActivateResponse with updated active/discoverable status.
        """
        data = await self._http.patch(f"/resources/{resource_id}/activate")
        return ActivateResponse.model_validate(data)

    async def get_payment_required(self, resource_id: str) -> PaymentRequiredPayload:
        """
        Retrieve the payment-required payload for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            PaymentRequiredPayload with pricing and payment details.
        """
        data = await self._http.get(f"/payment-required/{resource_id}")
        return PaymentRequiredPayload.model_validate(data or {})

    async def get_quota(self, resource_id: str) -> QuotaConfig:
        """
        Retrieve the quota configuration for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            QuotaConfig with per-wallet limits.
        """
        data = await self._http.get(f"/resources/{resource_id}/quota")
        return QuotaConfig.model_validate(data or {})

    async def set_quota(
        self,
        resource_id: str,
        *,
        max_purchases_per_wallet: int | None = None,
        max_calls_per_day_per_wallet: int | None = None,
    ) -> QuotaConfig:
        """
        Set or update the quota configuration for a resource.

        Args:
            resource_id: The resource UUID.
            max_purchases_per_wallet: Maximum purchases allowed per unique wallet address.
            max_calls_per_day_per_wallet: Maximum API calls per day per unique wallet.

        Returns:
            Updated QuotaConfig.
        """
        body: dict[str, Any] = {}
        if max_purchases_per_wallet is not None:
            body["max_purchases_per_wallet"] = max_purchases_per_wallet
        if max_calls_per_day_per_wallet is not None:
            body["max_calls_per_day_per_wallet"] = max_calls_per_day_per_wallet
        data = await self._http.put(f"/resources/{resource_id}/quota", json=body)
        return QuotaConfig.model_validate(data or {})

    async def delete_quota(self, resource_id: str) -> None:
        """
        Remove the quota configuration from a resource.

        Args:
            resource_id: The resource UUID.
        """
        await self._http.delete(f"/resources/{resource_id}/quota")

    async def get_webhook_secret(self, resource_id: str) -> WebhookSecretResponse:
        """
        Retrieve the HMAC secret used to verify webhook payloads for this resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            WebhookSecretResponse containing the webhook_secret string.
        """
        data = await self._http.get(f"/resources/{resource_id}/webhook-secret")
        return WebhookSecretResponse.model_validate(data)
