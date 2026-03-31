"""
Example: Subscription management workflow (vendor perspective).

This script demonstrates how a vendor manages subscription pricing plans,
monitors active subscribers, and handles subscription state — all without
any blockchain-specific details.

Run:
    MAINLAYER_API_KEY=ml_live_... python examples/subscription_flow.py
"""

from __future__ import annotations

import asyncio

from mainlayer import AsyncMainlayer, MainlayerError


async def main() -> None:
    async with AsyncMainlayer() as client:  # reads MAINLAYER_API_KEY from env
        # -------------------------------------------------------------------------
        # Step 1: Create a subscription-based resource
        # -------------------------------------------------------------------------
        print("Creating subscription resource...")
        resource = await client.resources.create(
            slug="premium-ai-service",
            type="api",
            price_usdc=4.99,
            fee_model="subscription",
            description="Unlimited access to premium AI features.",
            duration_seconds=30 * 24 * 3600,  # 30-day access window
            discoverable=True,
        )
        print(f"Resource created: {resource.slug} (id={resource.id})")

        # -------------------------------------------------------------------------
        # Step 2: Add multiple subscription tiers
        # -------------------------------------------------------------------------
        plans_data = [
            {
                "name": "Starter",
                "price_usdc": 4.99,
                "duration_seconds": 30 * 24 * 3600,
                "max_calls_per_day": 100,
            },
            {
                "name": "Pro",
                "price_usdc": 14.99,
                "duration_seconds": 30 * 24 * 3600,
                "max_calls_per_day": 1000,
            },
            {
                "name": "Enterprise",
                "price_usdc": 49.99,
                "duration_seconds": 30 * 24 * 3600,
                "max_calls_per_day": 10000,
            },
        ]

        created_plans = []
        for plan_data in plans_data:
            plan = await client.plans.create(
                resource.id,
                plan_data["name"],
                price_usdc=plan_data["price_usdc"],
                fee_model="subscription",
                duration_seconds=plan_data["duration_seconds"],
                max_calls_per_day=plan_data["max_calls_per_day"],
            )
            created_plans.append(plan)
            print(f"  Plan: {plan.name} — ${plan.price_usdc:.2f}/mo "
                  f"({plan_data['max_calls_per_day']:,} calls/day)")

        # -------------------------------------------------------------------------
        # Step 3: List plans to verify
        # -------------------------------------------------------------------------
        print("\nListing plans for resource:")
        plans = await client.plans.list(resource.id)
        for plan in plans:
            print(f"  {plan.name}: ${plan.price_usdc:.2f}")

        # -------------------------------------------------------------------------
        # Step 4: Update a plan's price
        # -------------------------------------------------------------------------
        if created_plans:
            starter = created_plans[0]
            updated = await client.plans.update(
                resource.id,
                starter.name,
                price_usdc=3.99,
            )
            print(f"\nUpdated '{updated.name}' price to ${updated.price_usdc:.2f}")

        # -------------------------------------------------------------------------
        # Step 5: Check active subscriptions
        # -------------------------------------------------------------------------
        print("\nFetching active subscriptions...")
        subscriptions = await client.subscriptions.list()
        if subscriptions:
            for sub in subscriptions:
                print(f"  Subscription {sub.id}: wallet={sub.payer_wallet}, "
                      f"status={sub.status}, plan={sub.plan_id}")
        else:
            print("  No active subscriptions yet.")

        # -------------------------------------------------------------------------
        # Step 6: Check access for a specific buyer
        # -------------------------------------------------------------------------
        test_wallet = "buyer_wallet_address_here"
        check = await client.entitlements.check(resource.id, payer_wallet=test_wallet)
        print(f"\nAccess check for {test_wallet[:16]}...: "
              f"{'allowed' if check.allowed else 'denied'}")
        if not check.allowed and check.reason:
            print(f"  Reason: {check.reason}")

        # -------------------------------------------------------------------------
        # Step 7: View analytics
        # -------------------------------------------------------------------------
        stats = await client.analytics.get(resource_id=resource.id)
        total_rev = stats.total_revenue_usdc or 0.0
        total_pay = stats.total_payments or 0
        print(f"\nAnalytics for {resource.slug}:")
        print(f"  Total revenue:  ${total_rev:.2f}")
        print(f"  Total payments: {total_pay}")
        print(f"  Unique payers:  {stats.unique_payers or 0}")

        # -------------------------------------------------------------------------
        # Step 8: Clean up — remove a deprecated plan
        # -------------------------------------------------------------------------
        if created_plans:
            deprecated = created_plans[-1]  # remove Enterprise plan for demo
            try:
                await client.plans.delete(resource.id, deprecated.name)
                print(f"\nDeleted deprecated plan: {deprecated.name}")
            except MainlayerError as e:
                print(f"Could not delete plan: {e.message}")

        print("\nSubscription flow complete.")


if __name__ == "__main__":
    asyncio.run(main())
