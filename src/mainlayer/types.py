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
    api = "api"
    file = "file"
    endpoint = "endpoint"
    page = "page"


class FeeModel(str, Enum):
    one_time = "one_time"
    subscription = "subscription"
    pay_per_call = "pay_per_call"


class DiscountType(str, Enum):
    percentage = "percentage"
    fixed = "fixed"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    id: str | None = None
    email: str | None = None
    message: str | None = None


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------


class ApiKey(BaseModel):
    id: str
    name: str
    key: str | None = None  # only present on creation
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


class Resource(BaseModel):
    id: str
    slug: str
    type: ResourceType
    price_usdc: float
    fee_model: FeeModel
    description: str | None = None
    callback_url: str | None = None
    credits_per_payment: int | None = None
    duration_seconds: int | None = None
    quota_calls: int | None = None
    discoverable: bool = False
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    owner_user_id: str | None = None


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------


class Plan(BaseModel):
    id: str
    resource_id: str
    name: str
    price_usdc: float
    duration_seconds: int
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------


class Payment(BaseModel):
    id: str
    resource_id: str
    payer_wallet: str
    amount_usdc: float | None = None
    fee_usdc: float | None = None
    net_usdc: float | None = None
    status: str | None = None
    tx_hash: str | None = None
    plan_id: str | None = None
    coupon_code: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Entitlements
# ---------------------------------------------------------------------------


class Entitlement(BaseModel):
    id: str
    resource_id: str
    payer_wallet: str
    status: str | None = None
    expires_at: datetime | None = None
    remaining_credits: int | None = None
    created_at: datetime | None = None


class EntitlementCheck(BaseModel):
    allowed: bool
    reason: str | None = None
    entitlement: Entitlement | None = None


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


class Subscription(BaseModel):
    id: str
    resource_id: str
    payer_wallet: str
    plan_id: str | None = None
    status: str | None = None
    current_period_end: datetime | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class AnalyticsDataPoint(BaseModel):
    date: str | None = None
    revenue_usdc: float | None = None
    payment_count: int | None = None
    unique_payers: int | None = None


class Analytics(BaseModel):
    total_revenue_usdc: float | None = None
    total_payments: int | None = None
    unique_payers: int | None = None
    data: list[AnalyticsDataPoint] = Field(default_factory=list)
    resource_id: str | None = None
    start_date: str | None = None
    end_date: str | None = None


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------


class Vendor(BaseModel):
    id: str | None = None
    user_id: str | None = None
    display_name: str | None = None
    description: str | None = None
    website_url: str | None = None
    logo_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


class Webhook(BaseModel):
    id: str
    url: str
    events: list[str] = Field(default_factory=list)
    resource_id: str | None = None
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Coupons
# ---------------------------------------------------------------------------


class Coupon(BaseModel):
    id: str
    code: str
    discount_type: DiscountType
    discount_value: float
    resource_ids: list[str] | None = None
    max_uses: int | None = None
    use_count: int = 0
    expires_at: datetime | None = None
    active: bool = True
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------


class Invoice(BaseModel):
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
