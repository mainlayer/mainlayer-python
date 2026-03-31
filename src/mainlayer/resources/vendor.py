"""Vendor resource — register and manage vendor profile."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mainlayer.types import Vendor, VendorRegisterResponse

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class VendorResource:
    """Synchronous vendor profile management."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def register(
        self,
        wallet_address: str,
        nonce: str,
        signed_message: str,
    ) -> VendorRegisterResponse:
        """
        Register a new vendor by proving ownership of a wallet address.

        Args:
            wallet_address: The vendor's wallet address.
            nonce: A unique nonce string used in the signed message.
            signed_message: Message signed with the wallet's private key
                            to prove ownership.

        Returns:
            VendorRegisterResponse with vendor_id and api_key.
        """
        body: dict[str, Any] = {
            "wallet_address": wallet_address,
            "nonce": nonce,
            "signed_message": signed_message,
        }
        data = self._http.post("/vendors/register", json=body)
        return VendorRegisterResponse.model_validate(data or {})

    def get(self) -> Vendor:
        """
        Retrieve the vendor profile for the authenticated account.

        Returns:
            Vendor profile data.
        """
        data = self._http.get("/vendor")
        return Vendor.model_validate(data or {})

    def update(
        self,
        *,
        display_name: str | None = None,
        description: str | None = None,
        website_url: str | None = None,
        logo_url: str | None = None,
    ) -> Vendor:
        """
        Update the vendor profile.

        Only provided fields are changed.

        Args:
            display_name: Public display name for the vendor.
            description: Short description of the vendor's offerings.
            website_url: Vendor's website URL.
            logo_url: URL to the vendor's logo image.

        Returns:
            The updated Vendor profile.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if description is not None:
            body["description"] = description
        if website_url is not None:
            body["website_url"] = website_url
        if logo_url is not None:
            body["logo_url"] = logo_url
        data = self._http.patch("/vendor", json=body)
        return Vendor.model_validate(data or {})


class AsyncVendorResource:
    """Asynchronous vendor profile management."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def register(
        self,
        wallet_address: str,
        nonce: str,
        signed_message: str,
    ) -> VendorRegisterResponse:
        """
        Register a new vendor by proving ownership of a wallet address.

        Args:
            wallet_address: The vendor's wallet address.
            nonce: A unique nonce string used in the signed message.
            signed_message: Message signed with the wallet's private key
                            to prove ownership.

        Returns:
            VendorRegisterResponse with vendor_id and api_key.
        """
        body: dict[str, Any] = {
            "wallet_address": wallet_address,
            "nonce": nonce,
            "signed_message": signed_message,
        }
        data = await self._http.post("/vendors/register", json=body)
        return VendorRegisterResponse.model_validate(data or {})

    async def get(self) -> Vendor:
        """
        Retrieve the vendor profile for the authenticated account.

        Returns:
            Vendor profile data.
        """
        data = await self._http.get("/vendor")
        return Vendor.model_validate(data or {})

    async def update(
        self,
        *,
        display_name: str | None = None,
        description: str | None = None,
        website_url: str | None = None,
        logo_url: str | None = None,
    ) -> Vendor:
        """
        Update the vendor profile.

        Args:
            display_name: Public display name.
            description: Short description.
            website_url: Vendor website URL.
            logo_url: Logo image URL.

        Returns:
            The updated Vendor profile.
        """
        body: dict[str, Any] = {}
        if display_name is not None:
            body["display_name"] = display_name
        if description is not None:
            body["description"] = description
        if website_url is not None:
            body["website_url"] = website_url
        if logo_url is not None:
            body["logo_url"] = logo_url
        data = await self._http.patch("/vendor", json=body)
        return Vendor.model_validate(data or {})
