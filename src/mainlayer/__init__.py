"""
mainlayer — Official Python SDK for Mainlayer payment infrastructure.

Mainlayer is payment infrastructure for AI agents and developers: create
accounts, set up paid resources, accept payments, and manage subscriptions
programmatically.

Quickstart::

    from mainlayer import Mainlayer

    client = Mainlayer(api_key="ml_live_...")

    # Sell access to your API
    resource = client.resources.create(
        slug="my-ai-tool",
        type="api",
        price_usdc=0.10,
        fee_model="pay_per_call",
    )

    # Check if a buyer has access
    check = client.entitlements.check(resource.id, payer_wallet="wallet123")

Async usage::

    from mainlayer import AsyncMainlayer

    async with AsyncMainlayer(api_key="ml_live_...") as client:
        resource = await client.resources.create(
            slug="my-ai-tool",
            type="api",
            price_usdc=0.10,
            fee_model="pay_per_call",
        )
"""

from mainlayer._exceptions import (
    AuthenticationError,
    ConflictError,
    MainlayerError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from mainlayer.client import AsyncMainlayer, Mainlayer
from mainlayer.types import (
    ActivateResponse,
    Analytics,
    AnalyticsDataPoint,
    ApiKey,
    Coupon,
    DiscountType,
    DiscoverResult,
    Entitlement,
    EntitlementCheck,
    FeeModel,
    Invoice,
    Payment,
    PaymentRequiredPayload,
    Plan,
    QuotaConfig,
    RegisterResponse,
    Resource,
    ResourceType,
    Subscription,
    SubscriptionApproveResponse,
    SubscriptionCancelResponse,
    TokenResponse,
    Vendor,
    VendorRegisterResponse,
    Webhook,
    WebhookSecretResponse,
)

__version__ = "0.1.0"

__all__ = [
    # Clients
    "Mainlayer",
    "AsyncMainlayer",
    # Exceptions
    "MainlayerError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    # Types
    "ActivateResponse",
    "Analytics",
    "AnalyticsDataPoint",
    "ApiKey",
    "Coupon",
    "DiscountType",
    "DiscoverResult",
    "Entitlement",
    "EntitlementCheck",
    "FeeModel",
    "Invoice",
    "Payment",
    "PaymentRequiredPayload",
    "Plan",
    "QuotaConfig",
    "RegisterResponse",
    "Resource",
    "ResourceType",
    "Subscription",
    "SubscriptionApproveResponse",
    "SubscriptionCancelResponse",
    "TokenResponse",
    "Vendor",
    "VendorRegisterResponse",
    "Webhook",
    "WebhookSecretResponse",
    # Version
    "__version__",
]
