"""Payments resource — execute and list payments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Payment

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class PaymentsResource:
    """Synchronous payment operations."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def pay(
        self,
        resource_id: str,
        payer_wallet: str,
        *,
        plan_id: str | None = None,
        coupon_code: str | None = None,
    ) -> Payment:
        """
        Execute a payment for a resource.

        Args:
            resource_id: The UUID of the resource to pay for.
            payer_wallet: The buyer's wallet address.
            plan_id: Optional plan ID to select a specific pricing tier.
            coupon_code: Optional coupon code for a discount.

        Returns:
            The resulting Payment record.
        """
        body: dict = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        if plan_id is not None:
            body["plan_id"] = plan_id
        if coupon_code is not None:
            body["coupon_code"] = coupon_code
        data = self._http.post("/pay", json=body)
        return Payment.model_validate(data)

    def list(self) -> list[Payment]:
        """
        List all payments for the authenticated account.

        Returns:
            List of Payment records.
        """
        data = self._http.get("/payments")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Payment.model_validate(item) for item in items]


class AsyncPaymentsResource:
    """Asynchronous payment operations."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def pay(
        self,
        resource_id: str,
        payer_wallet: str,
        *,
        plan_id: str | None = None,
        coupon_code: str | None = None,
    ) -> Payment:
        """
        Execute a payment for a resource.

        Args:
            resource_id: The UUID of the resource to pay for.
            payer_wallet: The buyer's wallet address.
            plan_id: Optional plan ID to select a specific pricing tier.
            coupon_code: Optional coupon code for a discount.

        Returns:
            The resulting Payment record.
        """
        body: dict = {"resource_id": resource_id, "payer_wallet": payer_wallet}
        if plan_id is not None:
            body["plan_id"] = plan_id
        if coupon_code is not None:
            body["coupon_code"] = coupon_code
        data = await self._http.post("/pay", json=body)
        return Payment.model_validate(data)

    async def list(self) -> list[Payment]:
        """
        List all payments for the authenticated account.

        Returns:
            List of Payment records.
        """
        data = await self._http.get("/payments")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Payment.model_validate(item) for item in items]
