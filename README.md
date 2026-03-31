# mainlayer-python

[![PyPI version](https://img.shields.io/pypi/v/mainlayer.svg)](https://pypi.org/project/mainlayer/)
[![Python versions](https://img.shields.io/pypi/pyversions/mainlayer.svg)](https://pypi.org/project/mainlayer/)
[![CI](https://github.com/mainlayer/mainlayer-python/actions/workflows/ci.yml/badge.svg)](https://github.com/mainlayer/mainlayer-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Mainlayer](https://mainlayer.fr) — payment infrastructure for AI agents and developers.

Create accounts, publish paid resources, accept payments, and manage subscriptions — all programmatically. Both AI agents and human developers can integrate in minutes.

## Quickstart

```bash
pip install mainlayer
```

```python
from mainlayer import Mainlayer

client = Mainlayer(api_key="ml_live_...")

resource = client.resources.create(
    slug="my-ai-tool",
    type="api",
    price_usdc=0.10,
    fee_model="pay_per_call",
)

check = client.entitlements.check(resource.id, payer_wallet="buyer_wallet_address")
print(check.allowed)  # True or False
```

That's it — your API is now behind a paywall.

## Installation

```bash
pip install mainlayer
```

Requires Python 3.10+.

## Authentication

Set your API key as an environment variable (recommended):

```bash
export MAINLAYER_API_KEY=ml_live_...
```

Or pass it directly:

```python
client = Mainlayer(api_key="ml_live_...")
```

You can also authenticate with email and password using JWT tokens:

```python
client = Mainlayer()
token = client.auth.login("you@example.com", "password")
client.set_token(token.access_token)
```

## Async support

All operations are available on `AsyncMainlayer`:

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

## API Reference

### Auth

```python
# Register a new account
client.auth.register(email, password, wallet_address=None)

# Log in and get a token
token = client.auth.login(email, password)
client.set_token(token.access_token)
```

### API Keys

```python
# Create (key value shown once)
key = client.api_keys.create(name="production")
print(key.key)  # store this securely

# List
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
    type="api",               # "api" | "file" | "endpoint" | "page"
    price_usdc=0.10,
    fee_model="pay_per_call", # "one_time" | "subscription" | "pay_per_call"
    description="Optional description",
    callback_url="https://myapp.com/webhook",
    credits_per_payment=1,    # for pay_per_call
    discoverable=True,        # appear in public marketplace
)

# List your resources
resources = client.resources.list()

# Get one
resource = client.resources.get(resource_id)

# Get public info (no auth required)
resource = client.resources.get_public(resource_id)

# Update
resource = client.resources.update(resource_id, price_usdc=0.15)

# Delete
client.resources.delete(resource_id)
```

### Payments

```python
# Pay for a resource
payment = client.payments.pay(
    resource_id=resource.id,
    payer_wallet="buyer_wallet_address",
    plan_id=None,        # optional: specific plan
    coupon_code=None,    # optional: discount code
)

# List payments
payments = client.payments.list()
```

### Entitlements

Check and list buyer access grants.

```python
# Check access (returns immediately, lightweight)
check = client.entitlements.check(resource_id, payer_wallet="wallet_address")
if check.allowed:
    # serve the request
    pass

# List entitlements
entitlements = client.entitlements.list(resource_id=resource_id)
```

### Plans

Add tiered pricing to a resource.

```python
# Create a plan
plan = client.plans.create(
    resource_id=resource.id,
    name="Monthly",
    price_usdc=9.99,
    duration_seconds=30 * 24 * 3600,
)

# List plans
plans = client.plans.list(resource_id=resource.id)
```

### Subscriptions

```python
subscriptions = client.subscriptions.list()
client.subscriptions.cancel(subscription_id)
```

### Analytics

```python
stats = client.analytics.get(
    start_date="2024-01-01",
    end_date="2024-12-31",
    resource_id=resource.id,  # optional filter
)
print(f"Total revenue: ${stats.total_revenue_usdc:.2f}")
print(f"Total payments: {stats.total_payments}")
```

### Vendor profile

```python
vendor = client.vendor.get()

vendor = client.vendor.update(
    display_name="Acme AI",
    description="AI tools for developers.",
    website_url="https://acme.ai",
)
```

### Webhooks

```python
webhook = client.webhooks.create(
    url="https://myapp.com/hooks/mainlayer",
    events=["payment.created", "entitlement.created"],
    resource_id=resource.id,  # optional scope
)

webhooks = client.webhooks.list()
client.webhooks.delete(webhook_id)
```

### Coupons

```python
coupon = client.coupons.create(
    code="LAUNCH50",
    discount_type="percentage",  # "percentage" | "fixed"
    discount_value=50,
    resource_ids=[resource.id],  # optional: restrict to specific resources
    max_uses=1000,
    expires_at="2025-12-31T23:59:59Z",
)

coupons = client.coupons.list()
```

### Discovery

Search the public Mainlayer marketplace. No authentication required.

```python
results = client.discover.search(
    q="image captioning",
    type="api",           # optional filter
    fee_model="pay_per_call",  # optional filter
    limit=20,
    offset=0,
)

for resource in results.items:
    print(f"{resource.slug}: ${resource.price_usdc:.2f}")
```

### Invoices

```python
invoices = client.invoices.list()
```

## Error handling

All errors raise `MainlayerError` (or a subclass):

```python
from mainlayer import MainlayerError, NotFoundError, RateLimitError

try:
    resource = client.resources.get("nonexistent-id")
except NotFoundError as e:
    print(f"Not found: {e.message}")
except RateLimitError:
    print("Rate limited — slow down")
except MainlayerError as e:
    print(f"API error {e.status_code}: {e.message} (code={e.code})")
```

Available exception types:

| Exception | Status code |
|-----------|-------------|
| `MainlayerError` | Base class for all errors |
| `AuthenticationError` | 401 |
| `PermissionError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `ValidationError` | 422 |
| `RateLimitError` | 429 |

The SDK automatically retries `429` and `5xx` responses up to 3 times with exponential backoff (0.5s, 1.0s, 2.0s).

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

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/mainlayer/
```

## License

MIT
