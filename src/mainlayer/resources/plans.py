"""Plans resource — manage pricing plans for a resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import FeeModel, Plan

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


def _build_plan_body(
    name: str,
    price_usdc: float,
    fee_model: FeeModel | str | None = None,
    credits_per_payment: int | None = None,
    duration_seconds: int | None = None,
    max_calls_per_day: int | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"name": name, "price_usdc": price_usdc}
    if fee_model is not None:
        body["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
    if credits_per_payment is not None:
        body["credits_per_payment"] = credits_per_payment
    if duration_seconds is not None:
        body["duration_seconds"] = duration_seconds
    if max_calls_per_day is not None:
        body["max_calls_per_day"] = max_calls_per_day
    return body


class PlansResource:
    """Synchronous plan management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self, resource_id: str) -> list[Plan]:
        """
        List all pricing plans for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            List of Plan objects.
        """
        data = self._http.get(f"/resources/{resource_id}/plans")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Plan.model_validate(item) for item in items]

    def create(
        self,
        resource_id: str,
        name: str,
        price_usdc: float,
        *,
        fee_model: FeeModel | str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        max_calls_per_day: int | None = None,
    ) -> Plan:
        """
        Create a new pricing plan for a resource.

        Args:
            resource_id: The resource UUID.
            name: Human-readable plan name (e.g., "Monthly", "Annual").
            price_usdc: Plan price in USD.
            fee_model: Billing model for this plan (inherits from resource if not set).
            credits_per_payment: Credits granted per payment under this plan.
            duration_seconds: How long access lasts after payment.
            max_calls_per_day: Maximum API calls per day for subscribers to this plan.

        Returns:
            The created Plan.
        """
        body = _build_plan_body(
            name, price_usdc,
            fee_model=fee_model,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            max_calls_per_day=max_calls_per_day,
        )
        data = self._http.post(f"/resources/{resource_id}/plans", json=body)
        return Plan.model_validate(data)

    def update(
        self,
        resource_id: str,
        plan_name: str,
        *,
        price_usdc: float | None = None,
        fee_model: FeeModel | str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        max_calls_per_day: int | None = None,
    ) -> Plan:
        """
        Update an existing plan by name.

        Args:
            resource_id: The resource UUID.
            plan_name: The name of the plan to update.
            price_usdc: New price in USD.
            fee_model: New billing model.
            credits_per_payment: New credits per payment.
            duration_seconds: New access duration in seconds.
            max_calls_per_day: New maximum calls per day.

        Returns:
            The updated Plan.
        """
        body: dict[str, Any] = {}
        if price_usdc is not None:
            body["price_usdc"] = price_usdc
        if fee_model is not None:
            body["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        if credits_per_payment is not None:
            body["credits_per_payment"] = credits_per_payment
        if duration_seconds is not None:
            body["duration_seconds"] = duration_seconds
        if max_calls_per_day is not None:
            body["max_calls_per_day"] = max_calls_per_day
        data = self._http.put(f"/resources/{resource_id}/plans/{plan_name}", json=body)
        return Plan.model_validate(data)

    def delete(self, resource_id: str, plan_name: str) -> None:
        """
        Delete a pricing plan by name.

        Args:
            resource_id: The resource UUID.
            plan_name: The name of the plan to delete.
        """
        self._http.delete(f"/resources/{resource_id}/plans/{plan_name}")


class AsyncPlansResource:
    """Asynchronous plan management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self, resource_id: str) -> list[Plan]:
        """
        List all pricing plans for a resource.

        Args:
            resource_id: The resource UUID.

        Returns:
            List of Plan objects.
        """
        data = await self._http.get(f"/resources/{resource_id}/plans")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Plan.model_validate(item) for item in items]

    async def create(
        self,
        resource_id: str,
        name: str,
        price_usdc: float,
        *,
        fee_model: FeeModel | str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        max_calls_per_day: int | None = None,
    ) -> Plan:
        """
        Create a new pricing plan for a resource.

        Args:
            resource_id: The resource UUID.
            name: Human-readable plan name.
            price_usdc: Plan price in USD.
            fee_model: Billing model for this plan.
            credits_per_payment: Credits granted per payment.
            duration_seconds: How long access lasts after payment.
            max_calls_per_day: Maximum API calls per day for subscribers.

        Returns:
            The created Plan.
        """
        body = _build_plan_body(
            name, price_usdc,
            fee_model=fee_model,
            credits_per_payment=credits_per_payment,
            duration_seconds=duration_seconds,
            max_calls_per_day=max_calls_per_day,
        )
        data = await self._http.post(f"/resources/{resource_id}/plans", json=body)
        return Plan.model_validate(data)

    async def update(
        self,
        resource_id: str,
        plan_name: str,
        *,
        price_usdc: float | None = None,
        fee_model: FeeModel | str | None = None,
        credits_per_payment: int | None = None,
        duration_seconds: int | None = None,
        max_calls_per_day: int | None = None,
    ) -> Plan:
        """
        Update an existing plan by name.

        Args:
            resource_id: The resource UUID.
            plan_name: The name of the plan to update.
            price_usdc: New price in USD.
            fee_model: New billing model.
            credits_per_payment: New credits per payment.
            duration_seconds: New access duration in seconds.
            max_calls_per_day: New maximum calls per day.

        Returns:
            The updated Plan.
        """
        body: dict[str, Any] = {}
        if price_usdc is not None:
            body["price_usdc"] = price_usdc
        if fee_model is not None:
            body["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        if credits_per_payment is not None:
            body["credits_per_payment"] = credits_per_payment
        if duration_seconds is not None:
            body["duration_seconds"] = duration_seconds
        if max_calls_per_day is not None:
            body["max_calls_per_day"] = max_calls_per_day
        data = await self._http.put(f"/resources/{resource_id}/plans/{plan_name}", json=body)
        return Plan.model_validate(data)

    async def delete(self, resource_id: str, plan_name: str) -> None:
        """
        Delete a pricing plan by name.

        Args:
            resource_id: The resource UUID.
            plan_name: The name of the plan to delete.
        """
        await self._http.delete(f"/resources/{resource_id}/plans/{plan_name}")
