from urllib.parse import urlparse

from mcp.server.auth.provider import AccessToken
from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider
from fastmcp.server.auth.auth import ClientRegistrationOptions
from pydantic import AnyHttpUrl
from starlette.routing import Route

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

    def get_routes(self, mcp_path: str | None = None) -> list:
        routes = super().get_routes(mcp_path)

        # Fix: FastMCP registers /.well-known/oauth-authorization-server but
        # RFC 8414 path-aware discovery requires it at
        # /.well-known/oauth-authorization-server{issuer_path} when the issuer
        # URL has a path component (e.g. /canvas). Add the path-aware route.
        if self.issuer_url:
            issuer_path = urlparse(str(self.issuer_url)).path.rstrip("/")
            if issuer_path and issuer_path != "/":
                for route in list(routes):
                    if (
                        isinstance(route, Route)
                        and route.path == "/.well-known/oauth-authorization-server"
                    ):
                        routes.append(
                            Route(
                                f"/.well-known/oauth-authorization-server{issuer_path}",
                                endpoint=route.endpoint,
                                methods=route.methods,
                            )
                        )
                        break

        return routes

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
