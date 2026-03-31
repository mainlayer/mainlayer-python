"""Analytics resource — revenue and usage metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import Analytics

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class AnalyticsResource:
    """Synchronous analytics access."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def get(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resource_id: str | None = None,
    ) -> Analytics:
        """
        Retrieve analytics data for the authenticated vendor.

        Args:
            start_date: ISO 8601 date string (e.g., "2024-01-01").
            end_date: ISO 8601 date string (e.g., "2024-12-31").
            resource_id: Filter metrics to a specific resource.

        Returns:
            Analytics summary with revenue and payment count data.
        """
        params: dict = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if resource_id is not None:
            params["resource_id"] = resource_id
        data = self._http.get("/analytics", params=params or None)
        return Analytics.model_validate(data or {})


class AsyncAnalyticsResource:
    """Asynchronous analytics access."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def get(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        resource_id: str | None = None,
    ) -> Analytics:
        """
        Retrieve analytics data for the authenticated vendor.

        Args:
            start_date: ISO 8601 date string (e.g., "2024-01-01").
            end_date: ISO 8601 date string (e.g., "2024-12-31").
            resource_id: Filter metrics to a specific resource.

        Returns:
            Analytics summary with revenue and payment count data.
        """
        params: dict = {}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if resource_id is not None:
            params["resource_id"] = resource_id
        data = await self._http.get("/analytics", params=params or None)
        return Analytics.model_validate(data or {})
