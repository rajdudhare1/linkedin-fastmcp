from __future__ import annotations

import argparse

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.oauth_callback import run_callback_server
from linkedin_fastmcp.server import create_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LinkedIn FastMCP server")
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--path", default="/mcp")
    parser.add_argument(
        "--oauth-callback-server",
        action="store_true",
        help="Listen for one OAuth callback, exchange the code, and print the access token",
    )
    parser.add_argument("--callback-host", default="127.0.0.1")
    parser.add_argument("--callback-port", type=int, default=8080)
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Print non-secret config and exit",
    )
    args = parser.parse_args()

    if args.show_config:
        config = load_config()
        print(f"LINKEDIN_CLIENT_ID set: {bool(config.client_id)}")
        print(f"LINKEDIN_CLIENT_SECRET set: {bool(config.client_secret)}")
        print(f"LINKEDIN_REDIRECT_URI: {config.redirect_uri}")
        print(f"LINKEDIN_ACCESS_TOKEN set: {bool(config.access_token)}")
        print(f"LINKEDIN_MEMBER_URN set: {bool(config.member_urn)}")
        print(f"LINKEDIN_SCOPES: {' '.join(config.scopes)}")
        print(f"LINKEDIN_API_VERSION: {config.api_version}")
        return

    if args.oauth_callback_server:
        run_callback_server(args.callback_host, args.callback_port)
        return

    mcp = create_server()
    if args.transport == "streamable-http":
        mcp.run(transport=args.transport, host=args.host, port=args.port, path=args.path)
    else:
        mcp.run(transport=args.transport)
