"""
MainlayerClient and AsyncMainlayerClient — top-level SDK entry points.

Both clients expose the same resource namespaces; the sync client uses
blocking httpx under the hood while the async client uses httpx.AsyncClient.
"""

from __future__ import annotations

import os
from typing import Any

from mainlayer._http import _DEFAULT_BASE_URL, AsyncTransport, SyncTransport
from mainlayer.resources.analytics import AnalyticsResource, AsyncAnalyticsResource
from mainlayer.resources.api_keys import ApiKeysResource, AsyncApiKeysResource
from mainlayer.resources.auth import AsyncAuthResource, AuthResource
from mainlayer.resources.coupons import AsyncCouponsResource, CouponsResource
from mainlayer.resources.discover import AsyncDiscoverResource, DiscoverResource
from mainlayer.resources.entitlements import AsyncEntitlementsResource, EntitlementsResource
from mainlayer.resources.invoices import AsyncInvoicesResource, InvoicesResource
from mainlayer.resources.payments import AsyncPaymentsResource, PaymentsResource
from mainlayer.resources.plans import AsyncPlansResource, PlansResource
from mainlayer.resources.resources import AsyncResourcesResource, ResourcesResource
from mainlayer.resources.subscriptions import AsyncSubscriptionsResource, SubscriptionsResource
from mainlayer.resources.vendor import AsyncVendorResource, VendorResource
from mainlayer.resources.webhooks import AsyncWebhooksResource, WebhooksResource


class Mainlayer:
    """
    Synchronous Mainlayer API client.

    All methods block the calling thread. For async applications, use
    ``AsyncMainlayer`` instead.

    Example::

        from mainlayer import Mainlayer

        client = Mainlayer(api_key="ml_live_...")

        # Create a resource
        resource = client.resources.create(
            slug="my-ai-tool",
            type="api",
            price_usdc=0.10,
            fee_model="pay_per_call",
        )

        # Check whether a buyer has access
        check = client.entitlements.check(resource.id, payer_wallet="wallet123")
        print(check.allowed)

    Args:
        api_key: Mainlayer API key. Falls back to the ``MAINLAYER_API_KEY``
                 environment variable if not provided.
        token: JWT access token (alternative to api_key, e.g., after login).
        base_url: Override the API base URL. Defaults to ``https://api.mainlayer.fr``.
        timeout: HTTP request timeout in seconds (default 30).
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        token: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("MAINLAYER_API_KEY")
        resolved_url = base_url or os.environ.get("MAINLAYER_BASE_URL", _DEFAULT_BASE_URL)

        self._http = SyncTransport(
            api_key=resolved_key,
            token=token,
            base_url=resolved_url,
            timeout=timeout,
        )

        # Resource namespaces
        self.auth = AuthResource(self._http)
        self.api_keys = ApiKeysResource(self._http)
        self.resources = ResourcesResource(self._http)
        self.payments = PaymentsResource(self._http)
        self.entitlements = EntitlementsResource(self._http)
        self.plans = PlansResource(self._http)
        self.subscriptions = SubscriptionsResource(self._http)
        self.analytics = AnalyticsResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.coupons = CouponsResource(self._http)
        self.invoices = InvoicesResource(self._http)
        self.discover = DiscoverResource(self._http)
        self.vendor = VendorResource(self._http)

    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key used for subsequent requests.

        Useful when rotating keys or switching between accounts.
        """
        self._http.set_auth(api_key=api_key)

    def set_token(self, token: str) -> None:
        """
        Update the bearer token used for subsequent requests.

        Typically called after ``client.auth.login()`` to switch from
        API-key auth to JWT auth.
        """
        self._http.set_auth(token=token)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> Mainlayer:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class AsyncMainlayer:
    """
    Asynchronous Mainlayer API client.

    All methods are coroutines. Use this client in async contexts (FastAPI,
    asyncio applications, Jupyter notebooks with ``asyncio`` event loops, etc.).

    Example::

        import asyncio
        from mainlayer import AsyncMainlayer

        async def main():
            client = AsyncMainlayer(api_key="ml_live_...")

            resource = await client.resources.create(
                slug="my-ai-tool",
                type="api",
                price_usdc=0.10,
                fee_model="pay_per_call",
            )
            print(resource.id)

            await client.aclose()

        asyncio.run(main())

    Args:
        api_key: Mainlayer API key. Falls back to the ``MAINLAYER_API_KEY``
                 environment variable if not provided.
        token: JWT access token (alternative to api_key).
        base_url: Override the API base URL.
        timeout: HTTP request timeout in seconds (default 30).
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        token: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("MAINLAYER_API_KEY")
        resolved_url = base_url or os.environ.get("MAINLAYER_BASE_URL", _DEFAULT_BASE_URL)

        self._http = AsyncTransport(
            api_key=resolved_key,
            token=token,
            base_url=resolved_url,
            timeout=timeout,
        )

        # Resource namespaces
        self.auth = AsyncAuthResource(self._http)
        self.api_keys = AsyncApiKeysResource(self._http)
        self.resources = AsyncResourcesResource(self._http)
        self.payments = AsyncPaymentsResource(self._http)
        self.entitlements = AsyncEntitlementsResource(self._http)
        self.plans = AsyncPlansResource(self._http)
        self.subscriptions = AsyncSubscriptionsResource(self._http)
        self.analytics = AsyncAnalyticsResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)
        self.coupons = AsyncCouponsResource(self._http)
        self.invoices = AsyncInvoicesResource(self._http)
        self.discover = AsyncDiscoverResource(self._http)
        self.vendor = AsyncVendorResource(self._http)

    def set_api_key(self, api_key: str) -> None:
        """Update the API key used for subsequent requests."""
        self._http.set_auth(api_key=api_key)

    def set_token(self, token: str) -> None:
        """Update the bearer token used for subsequent requests."""
        self._http.set_auth(token=token)

    async def aclose(self) -> None:
        """Close the underlying async HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> AsyncMainlayer:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
