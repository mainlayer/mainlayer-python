"""Subscriptions resource — manage recurring access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import Subscription, SubscriptionApproveResponse, SubscriptionCancelResponse

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class SubscriptionsResource:
    """Synchronous subscription management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self) -> list[Subscription]:
        """
        List all subscriptions for the authenticated account.

        Returns:
            List of Subscription objects.
        """
        data = self._http.get("/subscriptions")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Subscription.model_validate(item) for item in items]

    def approve(
        self,
        resource_id: str,
        payer_wallet: str,
        max_renewals: int,
        chain: str,
        signed_approval: str,
        delegate_token_account: str,
        signed_at: str,
        *,
        plan: str | None = None,
        trial_days: int | None = None,
    ) -> SubscriptionApproveResponse:
        """
        Approve a new subscription for a resource.

        This records the buyer's pre-authorization to be charged on a recurring
        basis. The vendor calls this after collecting the buyer's signed approval.

        Args:
            resource_id: The resource UUID being subscribed to.
            payer_wallet: The buyer's wallet address.
            max_renewals: Maximum number of automatic renewal charges allowed.
            chain: The blockchain network (e.g., "solana").
            signed_approval: Buyer's signed authorization for recurring charges.
            delegate_token_account: Token account delegated for recurring debits.
            signed_at: ISO 8601 timestamp when the approval was signed.
            plan: Optional plan name to subscribe to.
            trial_days: Optional number of trial days before billing starts.

        Returns:
            SubscriptionApproveResponse with the new subscription details.
        """
        body: dict[str, Any] = {
            "resource_id": resource_id,
            "payer_wallet": payer_wallet,
            "max_renewals": max_renewals,
            "chain": chain,
            "signed_approval": signed_approval,
            "delegate_token_account": delegate_token_account,
            "signed_at": signed_at,
        }
        if plan is not None:
            body["plan"] = plan
        if trial_days is not None:
            body["trial_days"] = trial_days
        data = self._http.post("/subscriptions/approve", json=body)
        return SubscriptionApproveResponse.model_validate(data or {})

    def cancel(
        self,
        resource_id: str,
        payer_wallet: str,
        signed_message: str,
    ) -> SubscriptionCancelResponse:
        """
        Cancel an active subscription.

        Args:
            resource_id: The resource UUID of the subscription to cancel.
            payer_wallet: The buyer's wallet address.
            signed_message: Buyer's signed message authorizing the cancellation.

        Returns:
            SubscriptionCancelResponse confirming the cancellation.
        """
        body: dict[str, Any] = {
            "resource_id": resource_id,
            "payer_wallet": payer_wallet,
            "signed_message": signed_message,
        }
        data = self._http.post("/subscriptions/cancel", json=body)
        return SubscriptionCancelResponse.model_validate(data or {})


class AsyncSubscriptionsResource:
    """Asynchronous subscription management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self) -> list[Subscription]:
        """
        List all subscriptions for the authenticated account.

        Returns:
            List of Subscription objects.
        """
        data = await self._http.get("/subscriptions")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Subscription.model_validate(item) for item in items]

    async def approve(
        self,
        resource_id: str,
        payer_wallet: str,
        max_renewals: int,
        chain: str,
        signed_approval: str,
        delegate_token_account: str,
        signed_at: str,
        *,
        plan: str | None = None,
        trial_days: int | None = None,
    ) -> SubscriptionApproveResponse:
        """
        Approve a new subscription for a resource.

        Args:
            resource_id: The resource UUID being subscribed to.
            payer_wallet: The buyer's wallet address.
            max_renewals: Maximum number of automatic renewal charges allowed.
            chain: The blockchain network (e.g., "solana").
            signed_approval: Buyer's signed authorization for recurring charges.
            delegate_token_account: Token account delegated for recurring debits.
            signed_at: ISO 8601 timestamp when the approval was signed.
            plan: Optional plan name to subscribe to.
            trial_days: Optional number of trial days before billing starts.

        Returns:
            SubscriptionApproveResponse with the new subscription details.
        """
        body: dict[str, Any] = {
            "resource_id": resource_id,
            "payer_wallet": payer_wallet,
            "max_renewals": max_renewals,
            "chain": chain,
            "signed_approval": signed_approval,
            "delegate_token_account": delegate_token_account,
            "signed_at": signed_at,
        }
        if plan is not None:
            body["plan"] = plan
        if trial_days is not None:
            body["trial_days"] = trial_days
        data = await self._http.post("/subscriptions/approve", json=body)
        return SubscriptionApproveResponse.model_validate(data or {})

    async def cancel(
        self,
        resource_id: str,
        payer_wallet: str,
        signed_message: str,
    ) -> SubscriptionCancelResponse:
        """
        Cancel an active subscription.

        Args:
            resource_id: The resource UUID of the subscription to cancel.
            payer_wallet: The buyer's wallet address.
            signed_message: Buyer's signed message authorizing the cancellation.

        Returns:
            SubscriptionCancelResponse confirming the cancellation.
        """
        body: dict[str, Any] = {
            "resource_id": resource_id,
            "payer_wallet": payer_wallet,
            "signed_message": signed_message,
        }
        data = await self._http.post("/subscriptions/cancel", json=body)
        return SubscriptionCancelResponse.model_validate(data or {})
