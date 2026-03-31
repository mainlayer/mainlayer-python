"""Resource modules for the Mainlayer SDK."""

from mainlayer.resources.analytics import AnalyticsResource, AsyncAnalyticsResource
from mainlayer.resources.api_keys import ApiKeysResource, AsyncApiKeysResource
from mainlayer.resources.auth import AsyncAuthResource, AuthResource
from mainlayer.resources.coupons import AsyncCouponsResource, CouponsResource
from mainlayer.resources.discover import AsyncDiscoverResource, DiscoverResource
from mainlayer.resources.entitlements import AsyncEntitlementsResource, EntitlementsResource
from mainlayer.resources.invoices import AsyncInvoicesResource, InvoicesResource
from mainlayer.resources.payments import AsyncPaymentsResource, PaymentsResource
from mainlayer.resources.plans import AsyncPlansResource, PlansResource
from mainlayer.resources.resources import AsyncResourcesResource, ResourcesResource
from mainlayer.resources.subscriptions import AsyncSubscriptionsResource, SubscriptionsResource
from mainlayer.resources.vendor import AsyncVendorResource, VendorResource
from mainlayer.resources.webhooks import AsyncWebhooksResource, WebhooksResource

__all__ = [
    "AnalyticsResource",
    "AsyncAnalyticsResource",
    "ApiKeysResource",
    "AsyncApiKeysResource",
    "AuthResource",
    "AsyncAuthResource",
    "CouponsResource",
    "AsyncCouponsResource",
    "DiscoverResource",
    "AsyncDiscoverResource",
    "EntitlementsResource",
    "AsyncEntitlementsResource",
    "InvoicesResource",
    "AsyncInvoicesResource",
    "PaymentsResource",
    "AsyncPaymentsResource",
    "PlansResource",
    "AsyncPlansResource",
    "ResourcesResource",
    "AsyncResourcesResource",
    "SubscriptionsResource",
    "AsyncSubscriptionsResource",
    "VendorResource",
    "AsyncVendorResource",
    "WebhooksResource",
    "AsyncWebhooksResource",
]
