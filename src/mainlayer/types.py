"""
Pydantic models for all Mainlayer API entities.

These models represent the canonical shape of data returned by the Mainlayer API.
All fields are optional where the API may omit them in partial responses.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ResourceType(str, Enum):
    """Type of vendored resource."""

    api = "api"
    file = "file"
    endpoint = "endpoint"
    page = "page"


class FeeModel(str, Enum):
    """Billing model for a resource."""

    one_time = "one_time"
    subscription = "subscription"
    pay_per_call = "pay_per_call"


class DiscountType(str, Enum):
    """Type of discount applied by a coupon."""

    percentage = "percentage"
    fixed = "fixed"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    """Response returned by /auth/login."""

    access_token: str
    """JWT bearer token to use for authenticated requests."""
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Response returned by /auth/register."""

    id: str | None = None
    """New account ID."""
    email: str | None = None
    """Registered email address."""
    message: str | None = None
    """Optional informational message from the API."""


# ---------------------------------------------------------------------------
# Vendor registration
# ---------------------------------------------------------------------------


class VendorRegisterResponse(BaseModel):
    """Response returned by /vendors/register."""

    vendor_id: str | None = None
    """Unique vendor identifier."""
    api_key: str | None = None
    """API key for the registered vendor (store this securely)."""
    next_step: str | None = None
    """Optional instruction for the next onboarding step."""


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------


class ApiKey(BaseModel):
    """An API key belonging to an account."""

    id: str
    """Unique key identifier."""
    name: str
    """Human-readable label for the key."""
    key: str | None = None
    """Raw secret value — only present on creation, cannot be retrieved again."""
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class Resource(BaseModel):
    """A vendored asset or API endpoint that buyers can pay to access."""

    id: str
    """Unique resource identifier."""
    slug: str
    """URL-friendly identifier, unique per vendor."""
    type: ResourceType
    """Resource category: api, file, endpoint, or page."""
    price_usdc: float
    """Price in USD."""
    fee_model: FeeModel
    """Billing model: one_time, subscription, or pay_per_call."""
    vendor_wallet: str | None = None
    """Vendor's wallet address that receives payments."""
    description: str | None = None
    """Human-readable description shown in marketplace discovery."""
    callback_url: str | None = None
    """URL notified when a payment succeeds."""
    credits_per_payment: int | None = None
    """Credits granted per payment (pay_per_call billing)."""
    duration_seconds: int | None = None
    """Access duration after payment (subscription billing)."""
    quota_calls: int | None = None
    """Maximum calls allowed per entitlement period."""
    overage_price_usdc: float | None = None
    """Per-call price once the quota is exhausted."""
    metadata: dict[str, Any] | None = None
    """Arbitrary key-value metadata stored with the resource."""
    discoverable: bool = False
    """Whether this resource appears in public marketplace search."""
    active: bool = True
    """Whether this resource is currently accepting payments."""
    facilitator_url: str | None = None
    """URL of the payment facilitator (returned by public endpoint)."""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    owner_user_id: str | None = None


class ActivateResponse(BaseModel):
    """Response returned by PATCH /resources/{id}/activate."""

    id: str
    active: bool
    discoverable: bool
    next_step: str | None = None


class QuotaConfig(BaseModel):
    """Per-resource quota configuration."""

    resource_id: str | None = None
    max_purchases_per_wallet: int | None = None
    """Maximum number of purchases allowed per unique wallet."""
    max_calls_per_day_per_wallet: int | None = None
    """Maximum API calls per day per unique wallet."""


class WebhookSecretResponse(BaseModel):
    """Response returned by GET /resources/{id}/webhook-secret."""

    webhook_secret: str
    """HMAC secret used to verify incoming webhook payloads."""


class PaymentRequiredPayload(BaseModel):
    """Payload returned by GET /payment-required/{id} (X402 protocol)."""

    resource_id: str | None = None
    price_usdc: float | None = None
    fee_model: str | None = None
    payment_url: str | None = None
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------


class Plan(BaseModel):
    """A named pricing tier attached to a resource."""

    id: str | None = None
    """Unique plan identifier."""
    resource_id: str | None = None
    name: str
    """Human-readable plan name (e.g., "Monthly", "Annual")."""
    price_usdc: float
    """Plan price in USD."""
    fee_model: FeeModel | None = None
    """Billing model for this plan (inherits from resource if not set)."""
    credits_per_payment: int | None = None
    """Credits granted per payment under this plan."""
    duration_seconds: int | None = None
    """Access duration in seconds."""
    max_calls_per_day: int | None = None
    """Maximum API calls per day for subscribers to this plan."""
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------


class Payment(BaseModel):
    """A completed payment record."""

    id: str
    resource_id: str
    payer_wallet: str
    amount_usdc: float | None = None
    """Gross amount paid in USD."""
    fee_usdc: float | None = None
    """Platform fee in USD."""
    net_usdc: float | None = None
    """Net amount received by the vendor in USD."""
    status: str | None = None
    tx_hash: str | None = None
    """On-chain transaction hash."""
    plan_id: str | None = None
    coupon_code: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Entitlements
# ---------------------------------------------------------------------------


class Entitlement(BaseModel):
    """An access grant held by a buyer for a specific resource."""

    id: str
    resource_id: str
    payer_wallet: str
    status: str | None = None
    """Entitlement status: active, expired, or revoked."""
    expires_at: datetime | None = None
    remaining_credits: int | None = None
    created_at: datetime | None = None


class EntitlementCheck(BaseModel):
    """Result of an entitlement access check."""

    allowed: bool
    """True if the wallet currently has valid access."""
    reason: str | None = None
    """Machine-readable reason when access is denied."""
    entitlement: Entitlement | None = None
    """Full entitlement record when access is allowed."""


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


class Subscription(BaseModel):
    """A recurring subscription held by a buyer."""

    id: str
    resource_id: str
    payer_wallet: str
    plan_id: str | None = None
    status: str | None = None
    """Subscription status: active, cancelled, or expired."""
    current_period_end: datetime | None = None
    trial_days: int | None = None
    max_renewals: int | None = None
    created_at: datetime | None = None


class SubscriptionApproveResponse(BaseModel):
    """Response returned by POST /subscriptions/approve."""

    id: str | None = None
    resource_id: str | None = None
    payer_wallet: str | None = None
    status: str | None = None
    message: str | None = None


class SubscriptionCancelResponse(BaseModel):
    """Response returned by POST /subscriptions/cancel."""

    message: str | None = None
    resource_id: str | None = None
    payer_wallet: str | None = None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class AnalyticsDataPoint(BaseModel):
    """A single time-series data point in an analytics response."""

    date: str | None = None
    revenue_usdc: float | None = None
    payment_count: int | None = None
    unique_payers: int | None = None


class Analytics(BaseModel):
    """Aggregated analytics for a vendor or resource."""

    total_revenue_usdc: float | None = None
    total_payments: int | None = None
    unique_payers: int | None = None
    data: list[AnalyticsDataPoint] = Field(default_factory=list)
    """Time-series breakdown of revenue and payment counts."""
    resource_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------


class Vendor(BaseModel):
    """A vendor profile associated with an account."""

    id: str | None = None
    """Unique vendor identifier."""
    user_id: str | None = None
    vendor_id: str | None = None
    """Alias for id returned by /vendors/register."""
    display_name: str | None = None
    description: str | None = None
    website_url: str | None = None
    logo_url: str | None = None
    wallet_address: str | None = None
    """On-chain wallet address associated with this vendor."""
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


class Webhook(BaseModel):
    """A registered webhook endpoint for event delivery."""

    id: str
    url: str
    """HTTPS URL that receives event notifications."""
    events: list[str] = Field(default_factory=list)
    """Event names subscribed to (e.g., "payment.created")."""
    resource_id: str | None = None
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Coupons
# ---------------------------------------------------------------------------


class Coupon(BaseModel):
    """A discount code that can be applied at checkout."""

    id: str
    code: str
    discount_type: DiscountType
    discount_value: float
    """Discount amount. For percentage, 10 = 10% off. For fixed, 5.00 = $5.00 off."""
    resource_ids: list[str] | None = None
    """Resource UUIDs this coupon applies to. None means all resources."""
    max_uses: int | None = None
    use_count: int = 0
    expires_at: datetime | None = None
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------


class Invoice(BaseModel):
    """A payment invoice record."""

    id: str
    payment_id: str | None = None
    resource_id: str | None = None
    payer_wallet: str | None = None
    amount_usdc: float | None = None
    status: str | None = None
    issued_at: datetime | None = None
    due_at: datetime | None = None


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class DiscoverResult(BaseModel):
    """Paginated search results from the public marketplace."""

    items: list[Resource] = Field(default_factory=list)
    total: int | None = None
    limit: int | None = None
    offset: int | None = None


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------


class ListResponse(BaseModel):
    """Generic list wrapper used when the API returns a plain list."""

    items: list[Any] = Field(default_factory=list)
