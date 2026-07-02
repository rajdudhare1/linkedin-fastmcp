from __future__ import annotations

import json
from urllib.parse import urlencode

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from linkedin_fastmcp.config import LinkedInConfig, load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.mcp_oauth import (
    create_state,
    exchange_code,
    resolve_callback,
)
from linkedin_fastmcp.oauth import AUTHORIZATION_URL
from linkedin_fastmcp.token_store import save_token_response
from linkedin_fastmcp.tools import register_tools


def create_server() -> FastMCP:
    mcp = FastMCP("linkedin_fastmcp")
    register_tools(mcp)

    # ------------------------------------------------------------------
    # MCP OAuth discovery  (RFC 8414 style)
    # ------------------------------------------------------------------

    @mcp.custom_route(
        "/.well-known/oauth-authorization-server", methods=["GET"], include_in_schema=False
    )
    async def oauth_metadata(request: Request) -> Response:
        base = _server_base_url(request)
        return JSONResponse(
            {
                "issuer": base,
                "authorization_endpoint": f"{base}/authorize",
                "token_endpoint": f"{base}/token",
                "response_types_supported": ["code"],
                "grant_types_supported": ["authorization_code"],
                "code_challenge_methods_supported": ["S256"],
                "registration_endpoint": None,
            }
        )

    # ------------------------------------------------------------------
    # /authorize  -- redirects browser to LinkedIn
    # ------------------------------------------------------------------

    @mcp.custom_route("/authorize", methods=["GET"], include_in_schema=False)
    async def authorize(request: Request) -> Response:
        config = load_config()
        if not config.client_id:
            return JSONResponse(
                {"error": "server_error", "error_description": "LINKEDIN_CLIENT_ID not configured"},
                status_code=500,
            )

        client_redirect_uri = request.query_params.get("redirect_uri", "")
        if client_redirect_uri:
            from urllib.parse import urlparse
            parsed_redirect = urlparse(client_redirect_uri)
            if parsed_redirect.hostname and parsed_redirect.hostname not in (
                "localhost", "127.0.0.1", "::1"
            ):
                return JSONResponse(
                    {
                        "error": "invalid_redirect_uri",
                        "error_description": "Only localhost redirect URIs are allowed",
                    },
                    status_code=400,
                )
        state, linkedin_state = create_state(client_redirect_uri)

        # Build LinkedIn authorization URL
        server_callback = f"{_server_base_url(request)}/callback"
        params = {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": server_callback,
            "scope": " ".join(config.scopes),
            "state": linkedin_state,
        }
        return RedirectResponse(f"{AUTHORIZATION_URL}?{urlencode(params)}")

    # ------------------------------------------------------------------
    # /callback  -- LinkedIn redirects here after member approval
    # ------------------------------------------------------------------

    @mcp.custom_route("/callback", methods=["GET"], include_in_schema=False)
    async def linkedin_oauth_callback(request: Request) -> Response:
        error = request.query_params.get("error")
        if error:
            description = request.query_params.get("error_description") or error
            return HTMLResponse(
                _html_page("LinkedIn Authorization Failed", description),
                status_code=400,
            )

        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if not code:
            return HTMLResponse(
                _html_page("LinkedIn Authorization Failed", "Missing authorization code."),
                status_code=400,
            )

        # Exchange LinkedIn code for LinkedIn access token
        config = load_config()
        # Use server's own callback URL for the exchange
        server_callback = f"{_server_base_url(request)}/callback"
        try:
            # Override redirect_uri for token exchange to match what we sent
            token = await _exchange_with_redirect(config, code, server_callback)
            save_token_response(token)
        except LinkedInAPIError as exc:
            return HTMLResponse(
                _html_page("LinkedIn Token Exchange Failed", str(exc)),
                status_code=502,
            )
        except (LinkedInFastMCPError, ValueError) as exc:
            return HTMLResponse(
                _html_page("LinkedIn Token Exchange Failed", str(exc)),
                status_code=500,
            )

        linkedin_access_token = token.get("access_token", "")

        # If this came from the MCP OAuth flow (has state), redirect to MCP client
        if state:
            try:
                mcp_code, client_redirect = resolve_callback(state, linkedin_access_token)
            except ValueError:
                # No pending MCP state -- fall back to standalone callback page
                return HTMLResponse(
                    _html_page(
                        "LinkedIn Authorization Complete",
                        "Access token saved. You can close this tab.",
                    )
                )

            if client_redirect:
                sep = "&" if "?" in client_redirect else "?"
                return RedirectResponse(f"{client_redirect}{sep}code={mcp_code}")

        return HTMLResponse(
            _html_page(
                "LinkedIn Authorization Complete",
                "Access token saved. You can close this tab and return to OpenCode.",
            )
        )

    # ------------------------------------------------------------------
    # /token  -- MCP client exchanges its code for a bearer token
    # ------------------------------------------------------------------

    @mcp.custom_route("/token", methods=["POST"], include_in_schema=False)
    async def token_endpoint(request: Request) -> Response:
        body = await request.body()
        try:
            # Accept both form-encoded and JSON
            content_type = request.headers.get("content-type", "")
            if "json" in content_type:
                data = json.loads(body)
            else:
                from urllib.parse import parse_qs

                raw = parse_qs(body.decode())
                data = {k: v[0] if len(v) == 1 else v for k, v in raw.items()}
        except Exception:
            return JSONResponse(
                {"error": "invalid_request", "error_description": "Malformed request body"},
                status_code=400,
            )

        grant_type = data.get("grant_type")
        code = data.get("code")

        if grant_type != "authorization_code" or not code:
            return JSONResponse(
                {
                    "error": "unsupported_grant_type",
                    "error_description": "Only authorization_code is supported",
                },
                status_code=400,
            )

        try:
            mcp_token = exchange_code(code)
        except ValueError:
            return JSONResponse(
                {"error": "invalid_grant", "error_description": "Invalid or expired code"},
                status_code=400,
            )

        return JSONResponse(
            {
                "access_token": mcp_token,
                "token_type": "Bearer",
                "expires_in": 86400,
            }
        )

    return mcp


async def _exchange_with_redirect(
    config: LinkedInConfig,
    code: str,
    redirect_uri: str,
) -> dict:
    """Exchange a LinkedIn authorization code with a specific redirect_uri."""
    import httpx

    from linkedin_fastmcp.errors import LinkedInAPIError
    from linkedin_fastmcp.oauth import TOKEN_URL

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(TOKEN_URL, data=data)

    if response.is_error:
        try:
            details = response.json()
        except ValueError:
            details = response.text
        raise LinkedInAPIError(response.status_code, "LinkedIn token exchange failed", details)
    return response.json()


def _server_base_url(request: Request) -> str:
    """Derive the external base URL from the request."""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    if scheme not in ("http", "https"):
        scheme = "http"
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{scheme}://{host}"


def _html_page(title: str, message: str) -> str:
    from html import escape
    return f"""
    <!doctype html>
    <html lang="en">
      <head><meta charset="utf-8"><title>{escape(title)}</title></head>
      <body style="font-family: system-ui, sans-serif; margin: 3rem; line-height: 1.5;">
        <h1>{escape(title)}</h1>
        <p>{escape(message)}</p>
      </body>
    </html>
    """
