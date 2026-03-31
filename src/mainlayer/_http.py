"""
HTTP transport layer for the Mainlayer SDK.

Provides both synchronous (SyncTransport) and asynchronous (AsyncTransport)
HTTP clients built on httpx. Both implement retry logic with exponential backoff
for 429 and 5xx responses.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from mainlayer._exceptions import MainlayerError

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "https://api.mainlayer.fr"
_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
_BACKOFF_BASE = 0.5  # seconds; doubles each retry: 0.5, 1.0, 2.0


def _should_retry(status_code: int) -> bool:
    return status_code in _RETRY_STATUS_CODES


def _backoff_seconds(attempt: int) -> float:
    """Exponential backoff: 0.5s, 1.0s, 2.0s for attempts 0, 1, 2."""
    return _BACKOFF_BASE * (2**attempt)


def _build_headers(api_key: str | None, token: str | None) -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    elif token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _raise_for_response(response: httpx.Response) -> None:
    """Raise MainlayerError for non-2xx responses with structured error info."""
    if response.is_success:
        return
    try:
        body = response.json()
    except Exception:
        body = {}

    # Extract error details from various API response shapes
    error_body = body.get("error", body)
    if isinstance(error_body, str):
        message = error_body
        code = None
    elif isinstance(error_body, dict):
        message = (
            error_body.get("message")
            or error_body.get("detail")
            or str(error_body)
        )
        code = error_body.get("code")
    else:
        message = response.text or f"HTTP {response.status_code}"
        code = None

    raise MainlayerError(
        message=message or f"HTTP {response.status_code}",
        status_code=response.status_code,
        code=code,
    )


# ---------------------------------------------------------------------------
# Synchronous transport
# ---------------------------------------------------------------------------


class SyncTransport:
    """
    Synchronous HTTP transport with retry logic.

    Thread-safe when each thread uses its own SyncTransport instance.
    Must be closed explicitly or used as a context manager.
    """

    def __init__(
        self,
        api_key: str | None = None,
        token: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._token = token
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(api_key, token),
            timeout=httpx.Timeout(timeout),
        )

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def set_auth(self, api_key: str | None = None, token: str | None = None) -> None:
        """Update the Authorization header (e.g., after login)."""
        self._api_key = api_key
        self._token = token
        auth_value = api_key or token
        if auth_value:
            self._client.headers["Authorization"] = f"Bearer {auth_value}"
        elif "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """Execute a request with automatic retry on transient errors."""
        url = path if path.startswith("http") else path
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = self._client.request(
                    method, url, params=params, json=json
                )
                if _should_retry(response.status_code) and attempt < _MAX_RETRIES - 1:
                    wait = _backoff_seconds(attempt)
                    logger.debug(
                        "Retrying %s %s (status=%s attempt=%s wait=%.1fs)",
                        method,
                        path,
                        response.status_code,
                        attempt + 1,
                        wait,
                    )
                    time.sleep(wait)
                    continue
                _raise_for_response(response)
                if response.status_code == 204 or not response.content:
                    return None
                return response.json()
            except MainlayerError:
                raise
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_backoff_seconds(attempt))
                    continue
            except httpx.RequestError as exc:
                raise MainlayerError(
                    message=f"Request failed: {exc}",
                    status_code=0,
                    code="request_error",
                ) from exc

        raise MainlayerError(
            message=f"Request timed out after {_MAX_RETRIES} attempts",
            status_code=0,
            code="timeout",
        ) from last_exc

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any = None, params: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, json=json, params=params)

    def patch(self, path: str, *, json: Any = None) -> Any:
        return self.request("PATCH", path, json=json)

    def put(self, path: str, *, json: Any = None) -> Any:
        return self.request("PUT", path, json=json)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)


# ---------------------------------------------------------------------------
# Asynchronous transport
# ---------------------------------------------------------------------------


class AsyncTransport:
    """
    Asynchronous HTTP transport with retry logic.

    Must be closed explicitly or used as an async context manager.
    """

    def __init__(
        self,
        api_key: str | None = None,
        token: str | None = None,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._token = token
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(api_key, token),
            timeout=httpx.Timeout(timeout),
        )

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def set_auth(self, api_key: str | None = None, token: str | None = None) -> None:
        """Update the Authorization header (e.g., after login)."""
        self._api_key = api_key
        self._token = token
        auth_value = api_key or token
        if auth_value:
            self._client.headers["Authorization"] = f"Bearer {auth_value}"
        elif "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        """Execute a request with automatic retry on transient errors."""
        import asyncio

        url = path if path.startswith("http") else path
        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = await self._client.request(
                    method, url, params=params, json=json
                )
                if _should_retry(response.status_code) and attempt < _MAX_RETRIES - 1:
                    wait = _backoff_seconds(attempt)
                    logger.debug(
                        "Retrying %s %s (status=%s attempt=%s wait=%.1fs)",
                        method,
                        path,
                        response.status_code,
                        attempt + 1,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                _raise_for_response(response)
                if response.status_code == 204 or not response.content:
                    return None
                return response.json()
            except MainlayerError:
                raise
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(_backoff_seconds(attempt))
                    continue
            except httpx.RequestError as exc:
                raise MainlayerError(
                    message=f"Request failed: {exc}",
                    status_code=0,
                    code="request_error",
                ) from exc

        raise MainlayerError(
            message=f"Request timed out after {_MAX_RETRIES} attempts",
            status_code=0,
            code="timeout",
        ) from last_exc

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, *, json: Any = None, params: dict[str, Any] | None = None) -> Any:
        return await self.request("POST", path, json=json, params=params)

    async def patch(self, path: str, *, json: Any = None) -> Any:
        return await self.request("PATCH", path, json=json)

    async def put(self, path: str, *, json: Any = None) -> Any:
        return await self.request("PUT", path, json=json)

    async def delete(self, path: str) -> Any:
        return await self.request("DELETE", path)
