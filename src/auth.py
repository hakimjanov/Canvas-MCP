from mcp.server.auth.provider import AccessToken
from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider
from fastmcp.server.auth.auth import ClientRegistrationOptions
from pydantic import AnyHttpUrl

from .config import Config


class CanvasOAuthProvider(InMemoryOAuthProvider):
    """
    OAuth 2.1 provider that also accepts a legacy static bearer token.

    - Claude connectors use the full OAuth 2.1 flow (DCR, PKCE, authorize, token).
    - Existing clients (e.g. poke.com) can continue using the static MCP_SERVER_TOKEN.
    """

    def __init__(self, base_url: str):
        super().__init__(
            base_url=AnyHttpUrl(base_url),
            client_registration_options=ClientRegistrationOptions(
                enabled=True,
                valid_scopes=["read", "write"],
            ),
            required_scopes=["read"],
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        # First, check if it's a valid OAuth-issued token
        result = await super().verify_token(token)
        if result is not None:
            return result

        # Fall back to legacy static token for existing clients
        if token == Config.MCP_SERVER_TOKEN:
            return AccessToken(
                token=token,
                client_id="legacy-static-client",
                scopes=["read", "write"],
            )

        return None
