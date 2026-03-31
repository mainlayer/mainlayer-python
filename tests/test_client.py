"""
Tests for the Mainlayer Python SDK.

Uses respx to mock HTTP calls — no real API requests are made.
"""

from __future__ import annotations

import json
import unittest.mock as mock

import pytest
import respx
from httpx import Response

from mainlayer import (
    AsyncMainlayer,
    FeeModel,
    Mainlayer,
    MainlayerError,
    ResourceType,
)

BASE_URL = "https://api.mainlayer.fr"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _json_response(data: dict | list, status_code: int = 200) -> Response:
    return Response(status_code, json=data)


def _resource_fixture(
    resource_id: str = "res-123",
    slug: str = "my-tool",
    rtype: str = "api",
    price: float = 0.10,
    fee_model: str = "pay_per_call",
) -> dict:
    return {
        "id": resource_id,
        "slug": slug,
        "type": rtype,
        "price_usdc": price,
        "fee_model": fee_model,
        "active": True,
        "discoverable": False,
    }


# ---------------------------------------------------------------------------
# Sync client — resources
# ---------------------------------------------------------------------------


class TestSyncResources:
    @respx.mock
    def test_create_resource(self) -> None:
        respx.post(f"{BASE_URL}/resources").mock(
            return_value=_json_response(_resource_fixture())
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.create(
            slug="my-tool",
            type=ResourceType.api,
            price_usdc=0.10,
            fee_model=FeeModel.pay_per_call,
        )

        assert resource.id == "res-123"
        assert resource.slug == "my-tool"
        assert resource.price_usdc == 0.10
        assert resource.type == ResourceType.api

    @respx.mock
    def test_create_resource_with_all_fields(self) -> None:
        route = respx.post(f"{BASE_URL}/resources").mock(
            return_value=_json_response(
                {
                    **_resource_fixture(),
                    "vendor_wallet": "wallet-v",
                    "credits_per_payment": 10,
                    "quota_calls": 1000,
                    "overage_price_usdc": 0.01,
                    "discoverable": True,
                    "callback_url": "https://example.com/webhook",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.create(
            slug="my-tool",
            type="api",
            price_usdc=0.10,
            fee_model="pay_per_call",
            vendor_wallet="wallet-v",
            description="A test tool",
            callback_url="https://example.com/webhook",
            credits_per_payment=10,
            quota_calls=1000,
            overage_price_usdc=0.01,
            metadata={"key": "val"},
            discoverable=True,
        )

        assert route.called
        sent = json.loads(route.calls[0].request.content)
        assert sent["vendor_wallet"] == "wallet-v"
        assert sent["credits_per_payment"] == 10
        assert sent["metadata"] == {"key": "val"}
        assert resource.credits_per_payment == 10

    @respx.mock
    def test_list_resources(self) -> None:
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response(
                [
                    _resource_fixture("res-1", "tool-a", price=1.0, fee_model="one_time"),
                    _resource_fixture("res-2", "tool-b", rtype="file", price=5.0),
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        resources = client.resources.list()

        assert len(resources) == 2
        assert resources[0].id == "res-1"
        assert resources[1].slug == "tool-b"

    @respx.mock
    def test_list_resources_paginated_response(self) -> None:
        """API can return {items: [...]} shape."""
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response({"items": [_resource_fixture()]})
        )

        client = Mainlayer(api_key="ml_test_key")
        resources = client.resources.list()
        assert len(resources) == 1

    @respx.mock
    def test_get_resource(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123").mock(
            return_value=_json_response(_resource_fixture(price=0.50))
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.get("res-123")

        assert resource.id == "res-123"
        assert resource.price_usdc == 0.50

    @respx.mock
    def test_get_public_resource(self) -> None:
        respx.get(f"{BASE_URL}/resources/public/res-123").mock(
            return_value=_json_response(
                {
                    **_resource_fixture(),
                    "facilitator_url": "https://facilitator.example.com",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.get_public("res-123")

        assert resource.id == "res-123"
        assert resource.facilitator_url == "https://facilitator.example.com"

    @respx.mock
    def test_update_resource(self) -> None:
        respx.put(f"{BASE_URL}/resources/res-123").mock(
            return_value=_json_response(_resource_fixture(price=0.25))
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.update("res-123", price_usdc=0.25)

        assert resource.price_usdc == 0.25

    @respx.mock
    def test_delete_resource(self) -> None:
        respx.delete(f"{BASE_URL}/resources/res-123").mock(
            return_value=Response(204)
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.resources.delete("res-123")

        assert result is None

    @respx.mock
    def test_activate_resource(self) -> None:
        respx.patch(f"{BASE_URL}/resources/res-123/activate").mock(
            return_value=_json_response(
                {"id": "res-123", "active": True, "discoverable": True, "next_step": None}
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.resources.activate("res-123")

        assert result.active is True
        assert result.id == "res-123"

    @respx.mock
    def test_get_payment_required(self) -> None:
        respx.get(f"{BASE_URL}/payment-required/res-123").mock(
            return_value=_json_response(
                {
                    "resource_id": "res-123",
                    "price_usdc": 0.10,
                    "fee_model": "pay_per_call",
                    "payment_url": "https://pay.mainlayer.fr/res-123",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        payload = client.resources.get_payment_required("res-123")

        assert payload.resource_id == "res-123"
        assert payload.price_usdc == 0.10

    @respx.mock
    def test_get_quota(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123/quota").mock(
            return_value=_json_response(
                {
                    "resource_id": "res-123",
                    "max_purchases_per_wallet": 5,
                    "max_calls_per_day_per_wallet": 100,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        quota = client.resources.get_quota("res-123")

        assert quota.max_purchases_per_wallet == 5
        assert quota.max_calls_per_day_per_wallet == 100

    @respx.mock
    def test_set_quota(self) -> None:
        route = respx.put(f"{BASE_URL}/resources/res-123/quota").mock(
            return_value=_json_response(
                {"resource_id": "res-123", "max_purchases_per_wallet": 10}
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        quota = client.resources.set_quota("res-123", max_purchases_per_wallet=10)

        assert quota.max_purchases_per_wallet == 10
        sent = json.loads(route.calls[0].request.content)
        assert sent["max_purchases_per_wallet"] == 10

    @respx.mock
    def test_delete_quota(self) -> None:
        respx.delete(f"{BASE_URL}/resources/res-123/quota").mock(
            return_value=Response(204)
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.resources.delete_quota("res-123")
        assert result is None

    @respx.mock
    def test_get_webhook_secret(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123/webhook-secret").mock(
            return_value=_json_response({"webhook_secret": "whsec_abc123"})
        )

        client = Mainlayer(api_key="ml_test_key")
        response = client.resources.get_webhook_secret("res-123")

        assert response.webhook_secret == "whsec_abc123"


# ---------------------------------------------------------------------------
# Sync client — entitlements
# ---------------------------------------------------------------------------


class TestSyncEntitlements:
    @respx.mock
    def test_check_entitlement_allowed(self) -> None:
        respx.get(f"{BASE_URL}/entitlements/check").mock(
            return_value=_json_response({"allowed": True})
        )

        client = Mainlayer(api_key="ml_test_key")
        check = client.entitlements.check("res-123", payer_wallet="wallet-abc")

        assert check.allowed is True

    @respx.mock
    def test_check_entitlement_denied(self) -> None:
        respx.get(f"{BASE_URL}/entitlements/check").mock(
            return_value=_json_response({"allowed": False, "reason": "no_entitlement"})
        )

        client = Mainlayer(api_key="ml_test_key")
        check = client.entitlements.check("res-123", payer_wallet="wallet-xyz")

        assert check.allowed is False
        assert check.reason == "no_entitlement"

    @respx.mock
    def test_list_entitlements(self) -> None:
        respx.get(f"{BASE_URL}/entitlements").mock(
            return_value=_json_response(
                [
                    {
                        "id": "ent-1",
                        "resource_id": "res-123",
                        "payer_wallet": "wallet-abc",
                        "status": "active",
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        entitlements = client.entitlements.list()

        assert len(entitlements) == 1
        assert entitlements[0].id == "ent-1"

    @respx.mock
    def test_list_entitlements_with_filters(self) -> None:
        route = respx.get(f"{BASE_URL}/entitlements").mock(
            return_value=_json_response([])
        )

        client = Mainlayer(api_key="ml_test_key")
        client.entitlements.list(resource_id="res-123", payer_wallet="wallet-abc")

        qs = route.calls[0].request.url.query
        assert b"resource_id=res-123" in qs
        assert b"payer_wallet=wallet-abc" in qs


# ---------------------------------------------------------------------------
# Sync client — payments
# ---------------------------------------------------------------------------


class TestSyncPayments:
    @respx.mock
    def test_pay(self) -> None:
        respx.post(f"{BASE_URL}/pay").mock(
            return_value=_json_response(
                {
                    "id": "pay-999",
                    "resource_id": "res-123",
                    "payer_wallet": "wallet-abc",
                    "status": "confirmed",
                    "amount_usdc": 0.10,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        payment = client.payments.pay("res-123", payer_wallet="wallet-abc")

        assert payment.id == "pay-999"
        assert payment.status == "confirmed"

    @respx.mock
    def test_pay_with_coupon(self) -> None:
        route = respx.post(f"{BASE_URL}/pay").mock(
            return_value=_json_response(
                {
                    "id": "pay-888",
                    "resource_id": "res-123",
                    "payer_wallet": "wallet-abc",
                    "status": "confirmed",
                    "coupon_code": "SAVE10",
                    "amount_usdc": 0.09,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        payment = client.payments.pay("res-123", payer_wallet="wallet-abc", coupon_code="SAVE10")

        assert payment.coupon_code == "SAVE10"
        body = json.loads(route.calls[0].request.content)
        assert body["coupon_code"] == "SAVE10"

    @respx.mock
    def test_list_payments(self) -> None:
        respx.get(f"{BASE_URL}/payments").mock(
            return_value=_json_response(
                [
                    {
                        "id": "pay-1",
                        "resource_id": "res-123",
                        "payer_wallet": "wallet-abc",
                        "amount_usdc": 0.10,
                        "status": "confirmed",
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        payments = client.payments.list()

        assert len(payments) == 1
        assert payments[0].id == "pay-1"


# ---------------------------------------------------------------------------
# Sync client — auth
# ---------------------------------------------------------------------------


class TestSyncAuth:
    @respx.mock
    def test_login(self) -> None:
        respx.post(f"{BASE_URL}/auth/login").mock(
            return_value=_json_response(
                {"access_token": "tok_abc123", "token_type": "bearer"}
            )
        )

        client = Mainlayer()
        token = client.auth.login("user@example.com", "secret")

        assert token.access_token == "tok_abc123"
        assert token.token_type == "bearer"

    @respx.mock
    def test_register(self) -> None:
        respx.post(f"{BASE_URL}/auth/register").mock(
            return_value=_json_response(
                {"id": "user-1", "email": "user@example.com"}
            )
        )

        client = Mainlayer()
        result = client.auth.register("user@example.com", "password123")

        assert result.email == "user@example.com"

    @respx.mock
    def test_login_then_set_token(self) -> None:
        respx.post(f"{BASE_URL}/auth/login").mock(
            return_value=_json_response({"access_token": "tok_xyz", "token_type": "bearer"})
        )
        route = respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response([])
        )

        client = Mainlayer()
        token = client.auth.login("user@example.com", "secret")
        client.set_token(token.access_token)
        client.resources.list()

        auth_header = route.calls[0].request.headers.get("authorization", "")
        assert "tok_xyz" in auth_header


# ---------------------------------------------------------------------------
# Sync client — vendor
# ---------------------------------------------------------------------------


class TestSyncVendor:
    @respx.mock
    def test_vendor_register(self) -> None:
        route = respx.post(f"{BASE_URL}/vendors/register").mock(
            return_value=_json_response(
                {
                    "vendor_id": "vnd-1",
                    "api_key": "ml_live_secretkey",
                    "next_step": "create_resource",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.vendor.register(
            wallet_address="wallet-abc",
            nonce="nonce-xyz",
            signed_message="sig-abc",
        )

        assert result.vendor_id == "vnd-1"
        assert result.api_key == "ml_live_secretkey"
        body = json.loads(route.calls[0].request.content)
        assert body["wallet_address"] == "wallet-abc"
        assert body["nonce"] == "nonce-xyz"

    @respx.mock
    def test_vendor_get(self) -> None:
        respx.get(f"{BASE_URL}/vendor").mock(
            return_value=_json_response(
                {"id": "vnd-1", "display_name": "Acme AI", "website_url": "https://acme.ai"}
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        vendor = client.vendor.get()

        assert vendor.id == "vnd-1"
        assert vendor.display_name == "Acme AI"

    @respx.mock
    def test_vendor_update(self) -> None:
        route = respx.patch(f"{BASE_URL}/vendor").mock(
            return_value=_json_response(
                {"id": "vnd-1", "display_name": "New Name", "description": "Updated"}
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        vendor = client.vendor.update(display_name="New Name", description="Updated")

        assert vendor.display_name == "New Name"
        body = json.loads(route.calls[0].request.content)
        assert body["display_name"] == "New Name"


# ---------------------------------------------------------------------------
# Sync client — discovery
# ---------------------------------------------------------------------------


class TestSyncDiscover:
    @respx.mock
    def test_search(self) -> None:
        respx.get(f"{BASE_URL}/discover").mock(
            return_value=_json_response(
                [
                    {
                        "id": "res-pub-1",
                        "slug": "public-tool",
                        "type": "api",
                        "price_usdc": 0.05,
                        "fee_model": "pay_per_call",
                        "active": True,
                        "discoverable": True,
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        results = client.discover.search(q="public tool")

        assert len(results.items) == 1
        assert results.items[0].slug == "public-tool"

    @respx.mock
    def test_search_with_filters(self) -> None:
        route = respx.get(f"{BASE_URL}/discover").mock(
            return_value=_json_response({"items": [], "total": 0})
        )

        client = Mainlayer(api_key="ml_test_key")
        results = client.discover.search(
            q="tool",
            type="api",
            fee_model="pay_per_call",
            limit=10,
            offset=5,
        )

        assert results.items == []
        qs = route.calls[0].request.url.query
        assert b"type=api" in qs
        assert b"limit=10" in qs
        assert b"offset=5" in qs

    @respx.mock
    def test_search_paginated_response(self) -> None:
        respx.get(f"{BASE_URL}/discover").mock(
            return_value=_json_response(
                {
                    "items": [_resource_fixture()],
                    "total": 1,
                    "limit": 20,
                    "offset": 0,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        results = client.discover.search()

        assert results.total == 1
        assert results.limit == 20


# ---------------------------------------------------------------------------
# Sync client — plans
# ---------------------------------------------------------------------------


class TestSyncPlans:
    @respx.mock
    def test_create_plan(self) -> None:
        respx.post(f"{BASE_URL}/resources/res-123/plans").mock(
            return_value=_json_response(
                {
                    "id": "plan-1",
                    "resource_id": "res-123",
                    "name": "Monthly",
                    "price_usdc": 9.99,
                    "duration_seconds": 2592000,
                    "active": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        plan = client.plans.create(
            "res-123",
            "Monthly",
            9.99,
            duration_seconds=2592000,
        )

        assert plan.id == "plan-1"
        assert plan.name == "Monthly"
        assert plan.price_usdc == 9.99

    @respx.mock
    def test_list_plans(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123/plans").mock(
            return_value=_json_response(
                [
                    {
                        "id": "plan-1",
                        "resource_id": "res-123",
                        "name": "Monthly",
                        "price_usdc": 9.99,
                        "duration_seconds": 2592000,
                        "active": True,
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        plans = client.plans.list("res-123")

        assert len(plans) == 1
        assert plans[0].name == "Monthly"

    @respx.mock
    def test_update_plan(self) -> None:
        route = respx.put(f"{BASE_URL}/resources/res-123/plans/Monthly").mock(
            return_value=_json_response(
                {
                    "id": "plan-1",
                    "resource_id": "res-123",
                    "name": "Monthly",
                    "price_usdc": 12.99,
                    "duration_seconds": 2592000,
                    "active": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        plan = client.plans.update("res-123", "Monthly", price_usdc=12.99)

        assert plan.price_usdc == 12.99
        body = json.loads(route.calls[0].request.content)
        assert body["price_usdc"] == 12.99

    @respx.mock
    def test_delete_plan(self) -> None:
        respx.delete(f"{BASE_URL}/resources/res-123/plans/Monthly").mock(
            return_value=Response(204)
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.plans.delete("res-123", "Monthly")
        assert result is None


# ---------------------------------------------------------------------------
# Sync client — subscriptions
# ---------------------------------------------------------------------------


class TestSyncSubscriptions:
    @respx.mock
    def test_list_subscriptions(self) -> None:
        respx.get(f"{BASE_URL}/subscriptions").mock(
            return_value=_json_response(
                [
                    {
                        "id": "sub-1",
                        "resource_id": "res-123",
                        "payer_wallet": "wallet-abc",
                        "status": "active",
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        subs = client.subscriptions.list()

        assert len(subs) == 1
        assert subs[0].id == "sub-1"

    @respx.mock
    def test_approve_subscription(self) -> None:
        route = respx.post(f"{BASE_URL}/subscriptions/approve").mock(
            return_value=_json_response(
                {
                    "id": "sub-new",
                    "resource_id": "res-123",
                    "payer_wallet": "wallet-abc",
                    "status": "active",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.subscriptions.approve(
            resource_id="res-123",
            payer_wallet="wallet-abc",
            max_renewals=12,
            chain="solana",
            signed_approval="sig-approval",
            delegate_token_account="token-acct",
            signed_at="2025-01-01T00:00:00Z",
            plan="Monthly",
        )

        assert result.id == "sub-new"
        body = json.loads(route.calls[0].request.content)
        assert body["resource_id"] == "res-123"
        assert body["max_renewals"] == 12
        assert body["plan"] == "Monthly"

    @respx.mock
    def test_cancel_subscription(self) -> None:
        route = respx.post(f"{BASE_URL}/subscriptions/cancel").mock(
            return_value=_json_response(
                {
                    "message": "cancelled",
                    "resource_id": "res-123",
                    "payer_wallet": "wallet-abc",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        result = client.subscriptions.cancel(
            resource_id="res-123",
            payer_wallet="wallet-abc",
            signed_message="sig-cancel",
        )

        assert result.message == "cancelled"
        body = json.loads(route.calls[0].request.content)
        assert body["signed_message"] == "sig-cancel"


# ---------------------------------------------------------------------------
# Sync client — error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @respx.mock
    def test_raises_mainlayer_error_on_404(self) -> None:
        respx.get(f"{BASE_URL}/resources/nonexistent").mock(
            return_value=Response(
                404,
                json={"error": {"message": "Resource not found", "code": "resource_not_found"}},
            )
        )

        client = Mainlayer(api_key="ml_test_key")

        with pytest.raises(MainlayerError) as exc_info:
            client.resources.get("nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.message.lower()

    @respx.mock
    def test_raises_mainlayer_error_on_401(self) -> None:
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=Response(401, json={"error": "Unauthorized"})
        )

        client = Mainlayer(api_key="invalid_key")

        with pytest.raises(MainlayerError) as exc_info:
            client.resources.list()

        assert exc_info.value.status_code == 401

    @respx.mock
    def test_raises_mainlayer_error_on_422(self) -> None:
        respx.post(f"{BASE_URL}/resources").mock(
            return_value=Response(
                422,
                json={"error": {"message": "slug is required", "code": "validation_error"}},
            )
        )

        client = Mainlayer(api_key="ml_test_key")

        with pytest.raises(MainlayerError) as exc_info:
            client.resources.create(slug="", type="api", price_usdc=0.10)

        assert exc_info.value.status_code == 422

    @respx.mock
    def test_raises_on_conflict_409(self) -> None:
        respx.post(f"{BASE_URL}/resources").mock(
            return_value=Response(
                409,
                json={"error": {"message": "slug already exists", "code": "conflict"}},
            )
        )

        client = Mainlayer(api_key="ml_test_key")

        with pytest.raises(MainlayerError) as exc_info:
            client.resources.create(slug="duplicate", type="api", price_usdc=0.10)

        assert exc_info.value.status_code == 409

    @respx.mock
    def test_error_with_string_body(self) -> None:
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        client = Mainlayer(api_key="ml_test_key")
        with mock.patch("time.sleep"):
            with pytest.raises(MainlayerError) as exc_info:
                client.resources.list()

        assert exc_info.value.status_code == 500

    @respx.mock
    def test_retries_on_500_then_succeeds(self) -> None:
        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return Response(500, json={"error": "Internal Server Error"})
            return Response(200, json=_resource_fixture())

        respx.get(f"{BASE_URL}/resources/res-1").mock(side_effect=side_effect)

        sleep_calls = []
        with mock.patch("time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            client = Mainlayer(api_key="ml_test_key")
            resource = client.resources.get("res-1")

        assert resource.id == "res-123"
        assert call_count == 2
        assert len(sleep_calls) == 1

    @respx.mock
    def test_exhausts_retries_on_persistent_500(self) -> None:
        respx.get(f"{BASE_URL}/resources/bad").mock(
            return_value=Response(500, json={"error": "always fails"})
        )

        client = Mainlayer(api_key="ml_test_key")
        with mock.patch("time.sleep"):
            with pytest.raises(MainlayerError) as exc_info:
                client.resources.get("bad")

        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# Sync client — webhooks
# ---------------------------------------------------------------------------


class TestWebhooks:
    @respx.mock
    def test_create_webhook(self) -> None:
        respx.post(f"{BASE_URL}/webhooks").mock(
            return_value=_json_response(
                {
                    "id": "wh-1",
                    "url": "https://myapp.com/hook",
                    "events": ["payment.created"],
                    "active": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        webhook = client.webhooks.create(
            url="https://myapp.com/hook",
            events=["payment.created"],
        )

        assert webhook.id == "wh-1"
        assert "payment.created" in webhook.events

    @respx.mock
    def test_list_webhooks(self) -> None:
        respx.get(f"{BASE_URL}/webhooks").mock(
            return_value=_json_response(
                [
                    {
                        "id": "wh-1",
                        "url": "https://myapp.com/hook",
                        "events": ["payment.created"],
                        "active": True,
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        webhooks = client.webhooks.list()

        assert len(webhooks) == 1
        assert webhooks[0].id == "wh-1"

    @respx.mock
    def test_delete_webhook(self) -> None:
        respx.delete(f"{BASE_URL}/webhooks/wh-1").mock(return_value=Response(204))

        client = Mainlayer(api_key="ml_test_key")
        result = client.webhooks.delete("wh-1")

        assert result is None


# ---------------------------------------------------------------------------
# Sync client — coupons
# ---------------------------------------------------------------------------


class TestCoupons:
    @respx.mock
    def test_create_coupon(self) -> None:
        respx.post(f"{BASE_URL}/coupons").mock(
            return_value=_json_response(
                {
                    "id": "coup-1",
                    "code": "SAVE20",
                    "discount_type": "percentage",
                    "discount_value": 20.0,
                    "use_count": 0,
                    "active": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        coupon = client.coupons.create(
            code="SAVE20",
            discount_type="percentage",
            discount_value=20.0,
        )

        assert coupon.code == "SAVE20"
        assert coupon.discount_value == 20.0

    @respx.mock
    def test_create_coupon_with_options(self) -> None:
        route = respx.post(f"{BASE_URL}/coupons").mock(
            return_value=_json_response(
                {
                    "id": "coup-2",
                    "code": "LAUNCH50",
                    "discount_type": "percentage",
                    "discount_value": 50.0,
                    "resource_ids": ["res-123"],
                    "max_uses": 100,
                    "use_count": 0,
                    "active": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        coupon = client.coupons.create(
            code="LAUNCH50",
            discount_type="percentage",
            discount_value=50.0,
            resource_ids=["res-123"],
            max_uses=100,
            expires_at="2025-12-31T23:59:59Z",
        )

        assert coupon.resource_ids == ["res-123"]
        body = json.loads(route.calls[0].request.content)
        assert body["expires_at"] == "2025-12-31T23:59:59Z"

    @respx.mock
    def test_list_coupons(self) -> None:
        respx.get(f"{BASE_URL}/coupons").mock(
            return_value=_json_response(
                [
                    {
                        "id": "coup-1",
                        "code": "SAVE20",
                        "discount_type": "percentage",
                        "discount_value": 20.0,
                        "use_count": 5,
                        "active": True,
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        coupons = client.coupons.list()

        assert len(coupons) == 1
        assert coupons[0].use_count == 5


# ---------------------------------------------------------------------------
# Sync client — analytics
# ---------------------------------------------------------------------------


class TestAnalytics:
    @respx.mock
    def test_get_analytics(self) -> None:
        respx.get(f"{BASE_URL}/analytics").mock(
            return_value=_json_response(
                {
                    "total_revenue_usdc": 42.50,
                    "total_payments": 850,
                    "unique_payers": 120,
                    "data": [],
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        analytics = client.analytics.get()

        assert analytics.total_revenue_usdc == 42.50
        assert analytics.total_payments == 850

    @respx.mock
    def test_get_analytics_with_filters(self) -> None:
        route = respx.get(f"{BASE_URL}/analytics").mock(
            return_value=_json_response({"total_revenue_usdc": 10.0, "data": []})
        )

        client = Mainlayer(api_key="ml_test_key")
        client.analytics.get(
            start_date="2024-01-01",
            end_date="2024-12-31",
            resource_id="res-123",
        )

        qs = route.calls[0].request.url.query
        assert b"start_date=2024-01-01" in qs
        assert b"resource_id=res-123" in qs

    @respx.mock
    def test_get_analytics_with_datapoints(self) -> None:
        respx.get(f"{BASE_URL}/analytics").mock(
            return_value=_json_response(
                {
                    "total_revenue_usdc": 5.0,
                    "total_payments": 50,
                    "data": [
                        {"date": "2024-01-01", "revenue_usdc": 2.5, "payment_count": 25},
                        {"date": "2024-01-02", "revenue_usdc": 2.5, "payment_count": 25},
                    ],
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        analytics = client.analytics.get(start_date="2024-01-01", end_date="2024-01-02")

        assert len(analytics.data) == 2
        assert analytics.data[0].date == "2024-01-01"
        assert analytics.data[1].revenue_usdc == 2.5


# ---------------------------------------------------------------------------
# Sync client — API Keys
# ---------------------------------------------------------------------------


class TestApiKeys:
    @respx.mock
    def test_create_api_key(self) -> None:
        respx.post(f"{BASE_URL}/api-keys").mock(
            return_value=_json_response(
                {
                    "id": "key-1",
                    "name": "production",
                    "key": "ml_live_secretvalue123",
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        api_key = client.api_keys.create("production")

        assert api_key.name == "production"
        assert api_key.key == "ml_live_secretvalue123"

    @respx.mock
    def test_list_api_keys(self) -> None:
        respx.get(f"{BASE_URL}/api-keys").mock(
            return_value=_json_response(
                [{"id": "key-1", "name": "production"}, {"id": "key-2", "name": "staging"}]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        keys = client.api_keys.list()

        assert len(keys) == 2
        assert keys[0].name == "production"

    @respx.mock
    def test_delete_api_key(self) -> None:
        respx.delete(f"{BASE_URL}/api-keys/key-1").mock(return_value=Response(204))

        client = Mainlayer(api_key="ml_test_key")
        result = client.api_keys.delete("key-1")

        assert result is None


# ---------------------------------------------------------------------------
# Sync client — invoices
# ---------------------------------------------------------------------------


class TestInvoices:
    @respx.mock
    def test_list_invoices(self) -> None:
        respx.get(f"{BASE_URL}/invoices").mock(
            return_value=_json_response(
                [
                    {
                        "id": "inv-1",
                        "payment_id": "pay-1",
                        "resource_id": "res-123",
                        "payer_wallet": "wallet-abc",
                        "amount_usdc": 9.99,
                        "status": "paid",
                    }
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        invoices = client.invoices.list()

        assert len(invoices) == 1
        assert invoices[0].id == "inv-1"
        assert invoices[0].amount_usdc == 9.99


# ---------------------------------------------------------------------------
# Async client
# ---------------------------------------------------------------------------


class TestAsyncClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_resource(self) -> None:
        respx.post(f"{BASE_URL}/resources").mock(
            return_value=_json_response(
                {
                    "id": "res-async-1",
                    "slug": "async-tool",
                    "type": "api",
                    "price_usdc": 0.20,
                    "fee_model": "pay_per_call",
                    "active": True,
                    "discoverable": False,
                }
            )
        )

        client = AsyncMainlayer(api_key="ml_test_key")
        resource = await client.resources.create(
            slug="async-tool",
            type="api",
            price_usdc=0.20,
            fee_model="pay_per_call",
        )
        await client.aclose()

        assert resource.id == "res-async-1"
        assert resource.slug == "async-tool"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_context_manager(self) -> None:
        respx.get(f"{BASE_URL}/entitlements/check").mock(
            return_value=_json_response({"allowed": True})
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            check = await client.entitlements.check("res-1", payer_wallet="wallet-1")

        assert check.allowed is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_retries_on_429(self) -> None:
        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return Response(429, json={"error": "rate_limit_exceeded"})
            return Response(200, json=[])

        respx.get(f"{BASE_URL}/payments").mock(side_effect=side_effect)

        with mock.patch("asyncio.sleep", return_value=None):
            async with AsyncMainlayer(api_key="ml_test_key") as client:
                payments = await client.payments.list()

        assert call_count == 2
        assert payments == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_login_and_set_token(self) -> None:
        respx.post(f"{BASE_URL}/auth/login").mock(
            return_value=_json_response(
                {"access_token": "jwt_token_xyz", "token_type": "bearer"}
            )
        )
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response([])
        )

        async with AsyncMainlayer() as client:
            token = await client.auth.login("user@example.com", "password")
            client.set_token(token.access_token)
            resources = await client.resources.list()

        assert token.access_token == "jwt_token_xyz"
        assert resources == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_activate_resource(self) -> None:
        respx.patch(f"{BASE_URL}/resources/res-123/activate").mock(
            return_value=_json_response(
                {"id": "res-123", "active": True, "discoverable": True}
            )
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            result = await client.resources.activate("res-123")

        assert result.active is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_webhook_secret(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123/webhook-secret").mock(
            return_value=_json_response({"webhook_secret": "whsec_async123"})
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            result = await client.resources.get_webhook_secret("res-123")

        assert result.webhook_secret == "whsec_async123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_vendor_register(self) -> None:
        respx.post(f"{BASE_URL}/vendors/register").mock(
            return_value=_json_response(
                {"vendor_id": "vnd-async", "api_key": "ml_live_abc"}
            )
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            result = await client.vendor.register(
                wallet_address="wallet-x",
                nonce="nonce-1",
                signed_message="sig-1",
            )

        assert result.vendor_id == "vnd-async"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_approve_subscription(self) -> None:
        respx.post(f"{BASE_URL}/subscriptions/approve").mock(
            return_value=_json_response(
                {"id": "sub-1", "status": "active", "resource_id": "res-123"}
            )
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            result = await client.subscriptions.approve(
                resource_id="res-123",
                payer_wallet="wallet-abc",
                max_renewals=12,
                chain="solana",
                signed_approval="sig",
                delegate_token_account="token-acct",
                signed_at="2025-01-01T00:00:00Z",
            )

        assert result.id == "sub-1"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_plan_delete(self) -> None:
        respx.delete(f"{BASE_URL}/resources/res-123/plans/Monthly").mock(
            return_value=Response(204)
        )

        async with AsyncMainlayer(api_key="ml_test_key") as client:
            result = await client.plans.delete("res-123", "Monthly")

        assert result is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_set_api_key(self) -> None:
        route = respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response([])
        )

        async with AsyncMainlayer(api_key="initial_key") as client:
            client.set_api_key("new_key")
            await client.resources.list()

        auth_header = route.calls[0].request.headers.get("authorization", "")
        assert "new_key" in auth_header
