"""
Tests for the Mainlayer Python SDK.

Uses respx to mock HTTP calls — no real API requests are made.
"""

from __future__ import annotations

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


# ---------------------------------------------------------------------------
# Sync client — resources
# ---------------------------------------------------------------------------


class TestSyncResources:
    @respx.mock
    def test_create_resource(self) -> None:
        respx.post(f"{BASE_URL}/resources").mock(
            return_value=_json_response(
                {
                    "id": "res-123",
                    "slug": "my-tool",
                    "type": "api",
                    "price_usdc": 0.10,
                    "fee_model": "pay_per_call",
                    "active": True,
                    "discoverable": False,
                }
            )
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
    def test_list_resources(self) -> None:
        respx.get(f"{BASE_URL}/resources").mock(
            return_value=_json_response(
                [
                    {
                        "id": "res-1",
                        "slug": "tool-a",
                        "type": "api",
                        "price_usdc": 1.0,
                        "fee_model": "one_time",
                        "active": True,
                        "discoverable": True,
                    },
                    {
                        "id": "res-2",
                        "slug": "tool-b",
                        "type": "file",
                        "price_usdc": 5.0,
                        "fee_model": "one_time",
                        "active": True,
                        "discoverable": False,
                    },
                ]
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        resources = client.resources.list()

        assert len(resources) == 2
        assert resources[0].id == "res-1"
        assert resources[1].slug == "tool-b"

    @respx.mock
    def test_get_resource(self) -> None:
        respx.get(f"{BASE_URL}/resources/res-123").mock(
            return_value=_json_response(
                {
                    "id": "res-123",
                    "slug": "my-tool",
                    "type": "api",
                    "price_usdc": 0.50,
                    "fee_model": "pay_per_call",
                    "active": True,
                    "discoverable": True,
                }
            )
        )

        client = Mainlayer(api_key="ml_test_key")
        resource = client.resources.get("res-123")

        assert resource.id == "res-123"
        assert resource.price_usdc == 0.50

    @respx.mock
    def test_update_resource(self) -> None:
        respx.patch(f"{BASE_URL}/resources/res-123").mock(
            return_value=_json_response(
                {
                    "id": "res-123",
                    "slug": "my-tool",
                    "type": "api",
                    "price_usdc": 0.25,
                    "fee_model": "pay_per_call",
                    "active": True,
                    "discoverable": True,
                }
            )
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
        # Verify coupon_code was sent in request body
        assert route.called
        sent_body = route.calls[0].request
        import json
        body = json.loads(sent_body.content)
        assert body["coupon_code"] == "SAVE10"


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
        plan = client.plans.create("res-123", "Monthly", 9.99, 2592000)

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
    def test_retries_on_500_then_succeeds(self) -> None:
        call_count = 0

        def side_effect(request):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return Response(500, json={"error": "Internal Server Error"})
            return Response(
                200,
                json={
                    "id": "res-1",
                    "slug": "tool",
                    "type": "api",
                    "price_usdc": 1.0,
                    "fee_model": "pay_per_call",
                    "active": True,
                    "discoverable": False,
                },
            )

        respx.get(f"{BASE_URL}/resources/res-1").mock(side_effect=side_effect)

        # Patch sleep to avoid slowing down tests
        sleep_calls = []
        import unittest.mock as mock
        with mock.patch("time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            client = Mainlayer(api_key="ml_test_key")
            resource = client.resources.get("res-1")

        assert resource.id == "res-1"
        assert call_count == 2
        assert len(sleep_calls) == 1  # slept once between retries


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
        import unittest.mock as mock

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


# ---------------------------------------------------------------------------
# Webhooks
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
    def test_delete_webhook(self) -> None:
        respx.delete(f"{BASE_URL}/webhooks/wh-1").mock(return_value=Response(204))

        client = Mainlayer(api_key="ml_test_key")
        result = client.webhooks.delete("wh-1")

        assert result is None


# ---------------------------------------------------------------------------
# Coupons
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


# ---------------------------------------------------------------------------
# Analytics
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

        request = route.calls[0].request
        assert b"start_date=2024-01-01" in request.url.query


# ---------------------------------------------------------------------------
# API Keys
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
