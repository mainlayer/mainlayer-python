"""
Example: Fully autonomous AI agent flow — from signup to accepting payments.

This script demonstrates the complete zero-human-in-the-loop workflow:
an AI agent can register, create a resource, and start earning — all
programmatically with no manual steps.

Run:
    python examples/agent_quickstart.py
"""

import asyncio

from mainlayer import AsyncMainlayer


async def main() -> None:
    # Step 1: Register a new account for this agent
    bootstrap = AsyncMainlayer()  # unauthenticated for registration
    print("Registering agent account...")
    await bootstrap.auth.register(
        email="agent-007@example.com",
        password="s3cure-p@ssword!",
    )

    # Step 2: Log in to get an access token
    token_resp = await bootstrap.auth.login(
        email="agent-007@example.com",
        password="s3cure-p@ssword!",
    )
    await bootstrap.aclose()

    # Step 3: Create an authenticated client using the token
    async with AsyncMainlayer(token=token_resp.access_token) as client:
        print(f"Logged in. Token type: {token_resp.token_type}")

        # Step 4: Create an API key for future use
        key = await client.api_keys.create(name="agent-primary")
        print(f"API key created: {key.id}")

        # Step 5: Update the vendor profile
        vendor = await client.vendor.update(
            display_name="Agent-007 Services",
            description="AI-powered analysis tools.",
        )
        print(f"Vendor profile set: {vendor.display_name}")

        # Step 6: Publish a resource for sale
        resource = await client.resources.create(
            slug="agent-007-analysis",
            type="api",
            price_usdc=0.01,
            fee_model="pay_per_call",
            description="Real-time analysis by Agent-007.",
            discoverable=True,
        )
        print(f"Resource published: {resource.slug} (${resource.price_usdc:.2f}/call)")
        print(f"Resource ID: {resource.id}")

        # Step 7: Create a coupon for early adopters
        coupon = await client.coupons.create(
            code="EARLYBIRD",
            discount_type="percentage",
            discount_value=50,
            resource_ids=[resource.id],
            max_uses=100,
        )
        print(f"Coupon created: {coupon.code} — {coupon.discount_value}% off")

        # Step 8: Check analytics (empty, but API is live)
        stats = await client.analytics.get()
        print(f"Total revenue so far: ${stats.total_revenue_usdc or 0:.2f}")

        print("\nAgent is fully operational and ready to accept payments!")
        print(f"Buyers can discover this resource by searching for: {resource.slug}")


if __name__ == "__main__":
    asyncio.run(main())
