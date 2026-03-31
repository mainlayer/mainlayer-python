"""Auth resource — register, login, and token management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mainlayer.types import RegisterResponse, TokenResponse

if TYPE_CHECKING:
    from mainlayer._http import AsyncTransport, SyncTransport


class AuthResource:
    """Synchronous auth operations."""

    def __init__(self, http: SyncTransport) -> None:
        self._http = http

    def register(
        self,
        email: str,
        password: str,
        wallet_address: str | None = None,
    ) -> RegisterResponse:
        """
        Register a new Mainlayer account.

        Args:
            email: Account email address.
            password: Account password (min 8 characters recommended).
            wallet_address: Optional wallet address to associate with the account.

        Returns:
            RegisterResponse with account details.
        """
        body: dict = {"email": email, "password": password}
        if wallet_address is not None:
            body["wallet_address"] = wallet_address
        data = self._http.post("/auth/register", json=body)
        return RegisterResponse.model_validate(data or {})

    def login(self, email: str, password: str) -> TokenResponse:
        """
        Log in and retrieve an access token.

        The returned token can be used to authenticate subsequent requests.
        Pass it as the ``token`` argument when constructing the client, or call
        ``client.set_token(token.access_token)`` after login.

        Args:
            email: Account email address.
            password: Account password.

        Returns:
            TokenResponse containing the access token.
        """
        data = self._http.post("/auth/login", json={"email": email, "password": password})
        return TokenResponse.model_validate(data)


class AsyncAuthResource:
    """Asynchronous auth operations."""

    def __init__(self, http: AsyncTransport) -> None:
        self._http = http

    async def register(
        self,
        email: str,
        password: str,
        wallet_address: str | None = None,
    ) -> RegisterResponse:
        """
        Register a new Mainlayer account.

        Args:
            email: Account email address.
            password: Account password.
            wallet_address: Optional wallet address to associate with the account.

        Returns:
            RegisterResponse with account details.
        """
        body: dict = {"email": email, "password": password}
        if wallet_address is not None:
            body["wallet_address"] = wallet_address
        data = await self._http.post("/auth/register", json=body)
        return RegisterResponse.model_validate(data or {})

    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Log in and retrieve an access token.

        Args:
            email: Account email address.
            password: Account password.

        Returns:
            TokenResponse containing the access token.
        """
        data = await self._http.post("/auth/login", json={"email": email, "password": password})
        return TokenResponse.model_validate(data)
