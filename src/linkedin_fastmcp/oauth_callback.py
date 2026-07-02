from __future__ import annotations

import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.oauth import exchange_code_for_token
from linkedin_fastmcp.token_store import save_token_response


class OAuthCallbackServer:
    def __init__(self) -> None:
        self.code: str | None = None
        self.state: str | None = None
        self.error: str | None = None
        self.error_description: str | None = None


def run_callback_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    result = OAuthCallbackServer()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            result.code = _first(params, "code")
            result.state = _first(params, "state")
            result.error = _first(params, "error")
            result.error_description = _first(params, "error_description")

            body = _response_html(result)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

    server = HTTPServer((host, port), Handler)
    print(f"Listening for LinkedIn OAuth callback on http://{host}:{port}/callback")
    print("Open the authorization URL, approve the app, and return here.")
    server.handle_request()
    server.server_close()

    if result.error:
        print(f"LinkedIn returned an error: {result.error}")
        if result.error_description:
            print(result.error_description)
        return

    if not result.code:
        print("No authorization code was received.")
        return

    print("Authorization code received. Exchanging it for an access token...")
    token = asyncio.run(exchange_code_for_token(load_config(), result.code))
    access_token = token.get("access_token")
    if not access_token:
        print("Token exchange returned unexpected response (no access_token key)")
        return

    token_file = save_token_response(token)
    print(f"\nAccess token saved to {token_file}")
    print("Your running MCP server can use it on the next tool call; no restart is required.")
    print("If you prefer environment variables, you can still add this to .env:")
    print(f"LINKEDIN_ACCESS_TOKEN={access_token[:8]}...{access_token[-4:]} (saved to file)")


def _first(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    if not values:
        return None
    return values[0]


def _response_html(result: OAuthCallbackServer) -> str:
    if result.error:
        message = result.error_description or result.error
        return f"""
        <html><body>
        <h1>LinkedIn authorization failed</h1>
        <p>{message}</p>
        <p>You can close this tab.</p>
        </body></html>
        """
    return """
    <html><body>
    <h1>LinkedIn authorization received</h1>
    <p>You can close this tab and return to your terminal.</p>
    </body></html>
    """
