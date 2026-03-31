"""Invoices resource — retrieve payment invoices."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Invoice

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class InvoicesResource:
    """Synchronous invoice access."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def list(self) -> list[Invoice]:
        """
        List all invoices for the authenticated account.

        Returns:
            List of Invoice objects.
        """
        data = self._http.get("/invoices")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Invoice.model_validate(item) for item in items]


class AsyncInvoicesResource:
    """Asynchronous invoice access."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def list(self) -> list[Invoice]:
        """
        List all invoices for the authenticated account.

        Returns:
            List of Invoice objects.
        """
        data = await self._http.get("/invoices")
        items = data if isinstance(data, list) else (data or {}).get("items", [])
        return [Invoice.model_validate(item) for item in items]
