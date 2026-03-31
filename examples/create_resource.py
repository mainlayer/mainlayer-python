"""
Example: Create a paid resource and add pricing plans.

Run:
    MAINLAYER_API_KEY=ml_live_... python examples/create_resource.py
"""

from mainlayer import Mainlayer

client = Mainlayer()

# Create a pay-per-call API resource
resource = client.resources.create(
    slug="image-caption-api",
    type="api",
    price_usdc=0.05,
    fee_model="pay_per_call",
    description="AI-powered image captioning — 5 cents per call.",
    callback_url="https://myapp.com/webhooks/mainlayer",
    credits_per_payment=1,
    discoverable=True,
)

print(f"Resource created!")
print(f"  ID:    {resource.id}")
print(f"  Slug:  {resource.slug}")
print(f"  Price: ${resource.price_usdc:.2f} per call")

# Add a bulk plan: 100 credits for $3
plan = client.plans.create(
    resource_id=resource.id,
    name="100-pack",
    price_usdc=3.00,
    duration_seconds=30 * 24 * 3600,  # 30 days
)

print(f"\nPlan created: {plan.name} — ${plan.price_usdc:.2f}")

# Register a webhook to receive payment notifications
webhook = client.webhooks.create(
    url="https://myapp.com/webhooks/mainlayer",
    events=["payment.created", "entitlement.created"],
    resource_id=resource.id,
)

print(f"\nWebhook registered: {webhook.id}")
print(f"  Listening for: {webhook.events}")

client.close()
