# mainlayer-python

[![PyPI version](https://img.shields.io/pypi/v/mainlayer.svg)](https://pypi.org/project/mainlayer/)
[![Python versions](https://img.shields.io/pypi/pyversions/mainlayer.svg)](https://pypi.org/project/mainlayer/)
[![CI](https://github.com/mainlayer/mainlayer-python/actions/workflows/ci.yml/badge.svg)](https://github.com/mainlayer/mainlayer-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Mainlayer](https://mainlayer.fr) — payment infrastructure for AI agents and developers.

Create accounts, publish paid resources, accept payments, and manage subscriptions — all programmatically. Both AI agents and human developers can integrate in minutes.

Full documentation: [docs.mainlayer.fr](https://docs.mainlayer.fr)

## Installation

```bash
pip install mainlayer
```

Requires Python 3.10+.

## Quickstart

```python
from mainlayer import Mainlayer

client = Mainlayer(api_key="ml_live_...")

# Create a resource (what you sell to buyers)
resource = client.resources.create(
    slug="my-ai-tool",
    type="api",
    price_usdc=0.10,
    fee_model="pay_per_call",
)

# Check whether a buyer currently has access
check = client.entitlements.check(resource.id, payer_wallet="buyer_wallet_address")
print(check.allowed)  # True or False
```

That's it — your API is now behind a paywall.

## Authentication

Set your API key as an environment variable (recommended):

```bash
export MAINLAYER_API_KEY=ml_live_...
```

Or pass it directly to the client:

```python
client = Mainlayer(api_key="ml_live_...")
```

You can also authenticate with email and password and use the returned JWT:

```python
client = Mainlayer()
token = client.auth.login("you@example.com", "password")
client.set_token(token.access_token)
```

## Async usage

All operations are available on `AsyncMainlayer`. Use it in any async context (FastAPI, asyncio, Jupyter notebooks, etc.):

```python
import asyncio
from mainlayer import AsyncMainlayer

async def main():
    async with AsyncMainlayer(api_key="ml_live_...") as client:
        resource = await client.resources.create(
            slug="my-ai-tool",
            type="api",
            price_usdc=0.10,
            fee_model="pay_per_call",
        )
        print(resource.id)

asyncio.run(main())
```

Every method on `Mainlayer` has a direct async equivalent on `AsyncMainlayer`.

## API Reference

### Auth

```python
# Register a new account
client.auth.register(email, password)

# Log in and get an access token
token = client.auth.login(email, password)
client.set_token(token.access_token)
```

### Vendor registration

```python
# Register a vendor profile linked to a wallet
result = client.vendor.register(
    wallet_address="wallet-abc",
    nonce="unique-nonce",
    signed_message="signature-proving-ownership",
)
print(result.vendor_id)
print(result.api_key)  # store securely

# Retrieve your vendor profile
vendor = client.vendor.get()

# Update your public vendor profile
vendor = client.vendor.update(
    display_name="Acme AI",
    description="AI tools for developers.",
    website_url="https://acme.ai",
)
```

### API Keys

```python
# Create (key value returned once)
key = client.api_keys.create(name="production")
print(key.key)  # store this securely — not shown again

# List (key values not included)
keys = client.api_keys.list()

# Delete
client.api_keys.delete(key_id)
```

### Resources

Resources are what you sell — API endpoints, files, pages, or any digital asset.

```python
# Create
resource = client.resources.create(
    slug="my-tool",
    type="api",                     # "api" | "file" | "endpoint" | "page"
    price_usdc=0.10,
    fee_model="pay_per_call",       # "one_time" | "subscription" | "pay_per_call"
    description="Optional description shown in discovery",
    callback_url="https://myapp.com/webhook",
    credits_per_payment=1,          # for pay_per_call
    duration_seconds=30 * 24 * 3600,  # for subscription
    quota_calls=1000,               # optional call quota
    overage_price_usdc=0.01,        # price per call after quota
    metadata={"env": "production"},
    discoverable=True,              # appear in public marketplace
)

# Activate (makes the resource available for purchase)
activated = client.resources.activate(resource_id)
print(activated.active, activated.discoverable)

# List your resources
resources = client.resources.list()

# Get one
resource = client.resources.get(resource_id)

# Get public info (no auth required)
resource = client.resources.get_public(resource_id)

# Update
resource = client.resources.update(resource_id, price_usdc=0.15)

# Deactivate
client.resources.delete(resource_id)
```

#### Resource quotas

```python
# Set per-wallet limits
quota = client.resources.set_quota(
    resource_id,
    max_purchases_per_wallet=10,
    max_calls_per_day_per_wallet=500,
)

# Retrieve current quota config
quota = client.resources.get_quota(resource_id)

# Remove quota limits
client.resources.delete_quota(resource_id)
```

#### Payment info

```python
# Retrieve the payment-required payload for a resource
payload = client.resources.get_payment_required(resource_id)
print(payload.price_usdc, payload.payment_url)

# Retrieve the webhook HMAC secret (use to verify event payloads)
secret = client.resources.get_webhook_secret(resource_id)
print(secret.webhook_secret)
```

### Payments

```python
# Pay for a resource
payment = client.payments.pay(
    resource_id=resource.id,
    payer_wallet="buyer_wallet_address",
    plan_id=None,        # optional: specific plan name
    coupon_code=None,    # optional: discount code
)

# List payments
payments = client.payments.list()
```

### Entitlements

Check and list buyer access grants.

```python
# Check access (lightweight, suitable for hot paths)
check = client.entitlements.check(resource_id, payer_wallet="wallet_address")
if check.allowed:
    # serve the request
    pass
else:
    print(check.reason)  # "no_entitlement" | "expired" | etc.

# List entitlements with optional filters
entitlements = client.entitlements.list(
    resource_id=resource_id,     # optional
    payer_wallet="wallet_address",  # optional
)
```

### Plans

Add tiered pricing to a resource.

```python
# Create a plan
plan = client.plans.create(
    resource_id=resource.id,
    name="Monthly",
    price_usdc=9.99,
    fee_model="subscription",
    duration_seconds=30 * 24 * 3600,
    max_calls_per_day=1000,
)

# List plans
plans = client.plans.list(resource_id=resource.id)

# Update a plan
plan = client.plans.update(resource_id, plan_name="Monthly", price_usdc=12.99)

# Delete a plan
client.plans.delete(resource_id, plan_name="Monthly")
```

### Subscriptions

```python
# List subscriptions for the authenticated account
subscriptions = client.subscriptions.list()

# Approve a new subscription (called after collecting buyer authorization)
result = client.subscriptions.approve(
    resource_id=resource.id,
    payer_wallet="buyer_wallet",
    max_renewals=12,
    chain="solana",
    signed_approval="<buyer_signed_approval>",
    delegate_token_account="<token_account>",
    signed_at="2025-01-01T00:00:00Z",
    plan="Monthly",       # optional: plan name
    trial_days=7,         # optional: trial period
)

# Cancel a subscription
result = client.subscriptions.cancel(
    resource_id=resource.id,
    payer_wallet="buyer_wallet",
    signed_message="<buyer_signed_cancellation>",
)
```

### Analytics

```python
stats = client.analytics.get(
    start_date="2024-01-01",   # optional ISO 8601 date
    end_date="2024-12-31",
    resource_id=resource.id,   # optional filter
)
print(f"Total revenue: ${stats.total_revenue_usdc:.2f}")
print(f"Total payments: {stats.total_payments}")

# Time-series breakdown
for point in stats.data:
    print(f"  {point.date}: ${point.revenue_usdc:.2f} ({point.payment_count} payments)")
```

### Webhooks

```python
# Register a webhook endpoint
webhook = client.webhooks.create(
    url="https://myapp.com/hooks/mainlayer",
    events=["payment.created", "entitlement.created", "entitlement.expired"],
    resource_id=resource.id,  # optional: scope to one resource
)

# List registered webhooks
webhooks = client.webhooks.list()

# Delete a webhook
client.webhooks.delete(webhook_id)
```

Verify incoming webhook payloads using the HMAC secret:

```python
import hashlib, hmac

secret = client.resources.get_webhook_secret(resource_id)
expected = hmac.new(
    secret.webhook_secret.encode(),
    request_body,
    hashlib.sha256,
).hexdigest()
assert hmac.compare_digest(expected, request_signature)
```

### Coupons

```python
# Create a discount coupon
coupon = client.coupons.create(
    code="LAUNCH50",
    discount_type="percentage",  # "percentage" | "fixed"
    discount_value=50,
    resource_ids=[resource.id],  # optional: restrict to specific resources
    max_uses=1000,
    expires_at="2025-12-31T23:59:59Z",
)

# List coupons
coupons = client.coupons.list()
```

### Discovery

Search the public Mainlayer marketplace. No authentication required.

```python
results = client.discover.search(
    q="image captioning",
    type="api",                  # optional filter
    fee_model="pay_per_call",    # optional filter
    limit=20,
    offset=0,
)

for resource in results.items:
    print(f"{resource.slug}: ${resource.price_usdc:.2f}")

print(f"Total results: {results.total}")
```

### Invoices

```python
invoices = client.invoices.list()
for invoice in invoices:
    print(f"{invoice.id}: ${invoice.amount_usdc:.2f} ({invoice.status})")
```

## Error handling

All errors raise `MainlayerError` (or a subclass):

```python
from mainlayer import MainlayerError, NotFoundError, RateLimitError, ValidationError

try:
    resource = client.resources.get("nonexistent-id")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except RateLimitError:
    print("Rate limited — slow down and retry")
except ValidationError as e:
    print(f"Invalid input: {e.message} (code={e.code})")
except MainlayerError as e:
    print(f"API error {e.status_code}: {e.message}")
```

Available exception classes:

| Exception | HTTP status |
|-----------|-------------|
| `MainlayerError` | Base class for all SDK errors |
| `AuthenticationError` | 401 |
| `PermissionError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `ValidationError` | 422 |
| `RateLimitError` | 429 |

The SDK automatically retries `429` and `5xx` responses up to 3 times with exponential backoff (0.5 s, 1.0 s, 2.0 s).

## Context manager usage

Both sync and async clients support context managers for automatic cleanup:

```python
# Sync
with Mainlayer(api_key="ml_live_...") as client:
    resource = client.resources.create(...)

# Async
async with AsyncMainlayer(api_key="ml_live_...") as client:
    resource = await client.resources.create(...)
```

## Examples

The `examples/` directory contains runnable scripts:

| File | Description |
|------|-------------|
| `vendor_onboarding.py` | Full onboarding: account, profile, resource, quota, plans, webhooks |
| `subscription_flow.py` | Create plans, manage subscriptions, check access |
| `create_resource.py` | Create a resource and attach a plan and webhook |
| `pay_for_resource.py` | Buyer workflow: discover, pay, verify access |
| `create_vendor.py` | Update vendor profile and create an API key |
| `agent_quickstart.py` | Fully autonomous agent onboarding with async |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (67 test cases)
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/mainlayer/
```

## Links

- Homepage: [mainlayer.fr](https://mainlayer.fr)
- Documentation: [docs.mainlayer.fr](https://docs.mainlayer.fr)
- Issues: [github.com/mainlayer/mainlayer-python/issues](https://github.com/mainlayer/mainlayer-python/issues)

## License

MIT
