"""Discover resource — search the public Mainlayer marketplace."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import DiscoverResult, FeeModel, Resource, ResourceType

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class DiscoverResource:
    """Synchronous resource discovery."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def search(
        self,
        *,
        q: str | None = None,
        type: ResourceType | str | None = None,
        fee_model: FeeModel | str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> DiscoverResult:
        """
        Search publicly discoverable resources in the Mainlayer marketplace.

        This endpoint does not require authentication.

        Args:
            q: Free-text search query.
            type: Filter by resource type — "api", "file", "endpoint", or "page".
            fee_model: Filter by fee model — "one_time", "subscription", or "pay_per_call".
            limit: Maximum number of results to return (default 20).
            offset: Pagination offset (default 0).

        Returns:
            DiscoverResult containing a list of matching resources and pagination info.
        """
        params: dict = {"limit": limit, "offset": offset}
        if q is not None:
            params["q"] = q
        if type is not None:
            params["type"] = type if isinstance(type, str) else type.value
        if fee_model is not None:
            params["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        data = self._http.get("/discover", params=params)

        # The /discover endpoint may return a list or a paginated object
        if isinstance(data, list):
            return DiscoverResult(items=[Resource.model_validate(item) for item in data])
        return DiscoverResult.model_validate(data or {})


class AsyncDiscoverResource:
    """Asynchronous resource discovery."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def search(
        self,
        *,
        q: str | None = None,
        type: ResourceType | str | None = None,
        fee_model: FeeModel | str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> DiscoverResult:
        """
        Search publicly discoverable resources in the Mainlayer marketplace.

        This endpoint does not require authentication.

        Args:
            q: Free-text search query.
            type: Filter by resource type.
            fee_model: Filter by fee model.
            limit: Maximum number of results to return (default 20).
            offset: Pagination offset (default 0).

        Returns:
            DiscoverResult containing matching resources and pagination info.
        """
        params: dict = {"limit": limit, "offset": offset}
        if q is not None:
            params["q"] = q
        if type is not None:
            params["type"] = type if isinstance(type, str) else type.value
        if fee_model is not None:
            params["fee_model"] = fee_model if isinstance(fee_model, str) else fee_model.value
        data = await self._http.get("/discover", params=params)

        if isinstance(data, list):
            return DiscoverResult(items=[Resource.model_validate(item) for item in data])
        return DiscoverResult.model_validate(data or {})
