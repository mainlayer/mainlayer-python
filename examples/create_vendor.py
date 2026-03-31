"""
Example: Register a new vendor account and set up a profile.

Run:
    MAINLAYER_API_KEY=ml_live_... python examples/create_vendor.py
"""

from mainlayer import Mainlayer

client = Mainlayer()  # reads MAINLAYER_API_KEY from environment

# Update your vendor profile so buyers can find you
vendor = client.vendor.update(
    display_name="Acme AI",
    description="Production-ready AI tools for developers and agents.",
    website_url="https://acme.ai",
)

print(f"Vendor profile: {vendor.display_name}")
print(f"Vendor ID:      {vendor.id}")

# Create an API key for your production environment
key = client.api_keys.create(name="production")

print(f"\nAPI key created: {key.name}")
print(f"Key ID:          {key.id}")
print(f"Key value:       {key.key}  <-- store this securely, it won't be shown again")

client.close()
