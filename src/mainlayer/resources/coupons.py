"""Coupons resource — create and manage discount codes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Coupon, DiscountType

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class CouponsResource:
    """Synchronous coupon management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self) -> list[Coupon]:
        """
        List all coupons for the authenticated vendor.

        Returns:
            List of Coupon objects.
        """
        data = self._http.get("/coupons")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Coupon.model_validate(item) for item in items]

    def create(
        self,
        code: str,
        discount_type: DiscountType | str,
        discount_value: float,
        *,
        resource_ids: list[str] | None = None,
        max_uses: int | None = None,
        expires_at: str | None = None,
    ) -> Coupon:
        """
        Create a new discount coupon.

        Args:
            code: The coupon code buyers enter at checkout (e.g., "LAUNCH50").
            discount_type: "percentage" (0-100) or "fixed" (dollar amount off).
            discount_value: The discount amount. For percentage, 10 = 10% off.
                            For fixed, 5.00 = $5.00 off.
            resource_ids: Optional list of resource UUIDs this coupon applies to.
                          If None, applies to all resources.
            max_uses: Optional maximum number of times this coupon can be used.
            expires_at: Optional ISO 8601 expiry timestamp (e.g., "2025-12-31T23:59:59Z").

        Returns:
            The created Coupon.
        """
        body: dict = {
            "code": code,
            "discount_type": discount_type if isinstance(discount_type, str) else discount_type.value,
            "discount_value": discount_value,
        }
        if resource_ids is not None:
            body["resource_ids"] = resource_ids
        if max_uses is not None:
            body["max_uses"] = max_uses
        if expires_at is not None:
            body["expires_at"] = expires_at
        data = self._http.post("/coupons", json=body)
        return Coupon.model_validate(data)


class AsyncCouponsResource:
    """Asynchronous coupon management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self) -> list[Coupon]:
        """
        List all coupons for the authenticated vendor.

        Returns:
            List of Coupon objects.
        """
        data = await self._http.get("/coupons")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Coupon.model_validate(item) for item in items]

    async def create(
        self,
        code: str,
        discount_type: DiscountType | str,
        discount_value: float,
        *,
        resource_ids: list[str] | None = None,
        max_uses: int | None = None,
        expires_at: str | None = None,
    ) -> Coupon:
        """
        Create a new discount coupon.

        Args:
            code: The coupon code buyers enter at checkout.
            discount_type: "percentage" or "fixed".
            discount_value: The discount amount.
            resource_ids: Optional list of resource UUIDs this applies to.
            max_uses: Optional maximum number of uses.
            expires_at: Optional ISO 8601 expiry timestamp.

        Returns:
            The created Coupon.
        """
        body: dict = {
            "code": code,
            "discount_type": discount_type if isinstance(discount_type, str) else discount_type.value,
            "discount_value": discount_value,
        }
        if resource_ids is not None:
            body["resource_ids"] = resource_ids
        if max_uses is not None:
            body["max_uses"] = max_uses
        if expires_at is not None:
            body["expires_at"] = expires_at
        data = await self._http.post("/coupons", json=body)
        return Coupon.model_validate(data)
