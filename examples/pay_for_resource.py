"""
Example: Discover a resource and pay for access (buyer workflow).

Run:
    MAINLAYER_API_KEY=ml_live_... python examples/pay_for_resource.py
"""

from mainlayer import Mainlayer

client = Mainlayer()

MY_WALLET = "wallet_abc123"  # replace with the buyer's wallet address

# Search the public marketplace for AI captioning tools
results = client.discover.search(q="image caption", type="api", limit=5)

print(f"Found {len(results.items)} resources:")
for r in results.items:
    print(f"  {r.slug}: ${r.price_usdc:.2f} ({r.fee_model})")

if not results.items:
    print("No results — try a different query.")
    client.close()
    raise SystemExit(0)

# Pay for the first result
resource = results.items[0]
print(f"\nPaying for: {resource.slug} (${resource.price_usdc:.2f})")

payment = client.payments.pay(
    resource_id=resource.id,
    payer_wallet=MY_WALLET,
)

print(f"Payment successful!")
print(f"  Payment ID: {payment.id}")
print(f"  Status:     {payment.status}")

# Verify access was granted
check = client.entitlements.check(resource.id, payer_wallet=MY_WALLET)
print(f"\nAccess check: {'allowed' if check.allowed else 'denied'}")

client.close()
