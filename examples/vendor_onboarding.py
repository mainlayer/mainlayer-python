"""
Example: Complete vendor onboarding workflow.

This script shows the full sequence for setting up a vendor account,
registering a wallet, creating a paid resource, and configuring access
controls — all programmatically.

Run:
    MAINLAYER_API_KEY=ml_live_... python examples/vendor_onboarding.py
"""

from __future__ import annotations

import asyncio

from mainlayer import AsyncMainlayer, MainlayerError


async def main() -> None:
    # -------------------------------------------------------------------------
    # Step 1: Register a new user account
    # -------------------------------------------------------------------------
    bootstrap = AsyncMainlayer()  # unauthenticated for registration
    print("Registering account...")

    try:
        await bootstrap.auth.register(
            email="vendor@example.com",
            password="s3cure-p@ssword!",
        )
        print("Account registered.")
    except MainlayerError as e:
        if "already" in (e.message or "").lower():
            print("Account already exists, continuing with login.")
        else:
            raise

    # -------------------------------------------------------------------------
    # Step 2: Log in and obtain an access token
    # -------------------------------------------------------------------------
    token_resp = await bootstrap.auth.login(
        email="vendor@example.com",
        password="s3cure-p@ssword!",
    )
    await bootstrap.aclose()
    print(f"Logged in. Token type: {token_resp.token_type}")

    # -------------------------------------------------------------------------
    # Step 3: Set up the authenticated client
    # -------------------------------------------------------------------------
    async with AsyncMainlayer(token=token_resp.access_token) as client:
        # Step 4: Update vendor profile so buyers can find you
        vendor = await client.vendor.update(
            display_name="Example AI",
            description="Production-ready AI tools for developers and agents.",
            website_url="https://example.ai",
        )
        print(f"\nVendor profile updated: {vendor.display_name}")

        # Step 5: Create a permanent API key for future use
        key = await client.api_keys.create(name="production")
        print(f"\nAPI key created: {key.name} (id={key.id})")
        print(f"  Key value: {key.key}  <-- store this securely")

        # Step 6: Create a pay-per-call resource
        resource = await client.resources.create(
            slug="example-ai-api",
            type="api",
            price_usdc=0.05,
            fee_model="pay_per_call",
            description="Powerful AI processing — 5 cents per call.",
            callback_url="https://example.ai/webhooks/mainlayer",
            credits_per_payment=1,
            discoverable=True,
        )
        print(f"\nResource created: {resource.slug} (${resource.price_usdc:.2f}/call)")
        print(f"  Resource ID: {resource.id}")

        # Step 7: Activate the resource so buyers can purchase it
        activated = await client.resources.activate(resource.id)
        print(f"\nResource activated: active={activated.active}, discoverable={activated.discoverable}")

        # Step 8: Set per-wallet quotas to prevent abuse
        quota = await client.resources.set_quota(
            resource.id,
            max_purchases_per_wallet=100,
            max_calls_per_day_per_wallet=1000,
        )
        print(f"\nQuota set: max_purchases={quota.max_purchases_per_wallet}, "
              f"max_calls/day={quota.max_calls_per_day_per_wallet}")

        # Step 9: Create tiered plans for bulk buyers
        monthly_plan = await client.plans.create(
            resource.id,
            "Monthly",
            price_usdc=9.99,
            fee_model="subscription",
            duration_seconds=30 * 24 * 3600,
            max_calls_per_day=500,
        )
        print(f"\nPlan created: {monthly_plan.name} — ${monthly_plan.price_usdc:.2f}/mo")

        # Step 10: Create a launch coupon
        coupon = await client.coupons.create(
            code="LAUNCH50",
            discount_type="percentage",
            discount_value=50,
            resource_ids=[resource.id],
            max_uses=200,
            expires_at="2025-12-31T23:59:59Z",
        )
        print(f"\nCoupon created: {coupon.code} — {coupon.discount_value:.0f}% off "
              f"(max {coupon.max_uses} uses)")

        # Step 11: Register a webhook for payment notifications
        webhook = await client.webhooks.create(
            url="https://example.ai/webhooks/mainlayer",
            events=["payment.created", "entitlement.created", "entitlement.expired"],
            resource_id=resource.id,
        )
        print(f"\nWebhook registered: {webhook.id}")
        print(f"  Listening for: {webhook.events}")

        # Step 12: Retrieve the webhook HMAC secret for payload verification
        secret = await client.resources.get_webhook_secret(resource.id)
        print(f"\nWebhook secret retrieved (first 8 chars): {secret.webhook_secret[:8]}...")

        print("\nOnboarding complete. Your resource is live and ready to accept payments.")
        print(f"Buyers can discover it by searching for: {resource.slug}")


if __name__ == "__main__":
    asyncio.run(main())
