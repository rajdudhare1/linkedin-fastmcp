from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.oauth import build_authorization_url, exchange_code_for_token
from linkedin_fastmcp.token_store import default_token_file, save_member_urn, save_token_response


def register_auth_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"auth"})
    def linkedin_get_auth_url(state: str | None = None) -> dict[str, Any]:
        """Create a LinkedIn OAuth authorization URL for the configured app."""
        try:
            return {"ok": True, **build_authorization_url(load_config(), state=state)}
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"auth"})
    async def linkedin_exchange_code_for_token(code: str) -> dict[str, Any]:
        """Exchange a LinkedIn OAuth authorization code for an access token."""
        try:
            token = await exchange_code_for_token(load_config(), code)
            token_file = save_token_response(token)
            safe = {k: v for k, v in token.items() if k != "access_token"}
            safe["access_token_preview"] = token.get("access_token", "")[:8] + "..."
            return {"ok": True, "token": safe, "token_file": str(token_file)}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"auth"})
    def linkedin_get_supported_actions() -> dict[str, Any]:
        """Show configured scopes and the actions this server can try to perform."""
        config = load_config()
        scopes = set(config.scopes)
        return {
            "ok": True,
            "configured_scopes": sorted(scopes),
            "has_access_token": config.has_access_token,
            "actions": {
                "profile_userinfo": {
                    "available_when": ["openid profile email", "or r_profile_basicinfo"],
                    "configured": "openid" in scopes or "r_profile_basicinfo" in scopes,
                },
                "create_personal_post": {
                    "available_when": ["w_member_social"],
                    "configured": "w_member_social" in scopes,
                },
                "image_post": {
                    "available_when": ["w_member_social"],
                    "configured": "w_member_social" in scopes,
                    "note": "Register upload, upload binary, then create post.",
                },
                "create_comment": {
                    "available_when": ["LinkedIn social actions API access"],
                    "configured": "w_member_social" in scopes,
                    "note": "LinkedIn may require additional approval beyond w_member_social.",
                },
                "like_or_repost": {
                    "available_when": ["w_member_social", "LinkedIn social actions API access"],
                    "configured": "w_member_social" in scopes,
                    "note": "Reactions and reposts can require LinkedIn product approval.",
                },
                "read_posts_and_engagement": {
                    "available_when": ["r_member_social or approved partner APIs"],
                    "configured": "r_member_social" in scopes,
                    "note": "r_member_social is restricted and may be unavailable for your app.",
                },
                "organization_pages": {
                    "available_when": [
                        "w_organization_social/r_organization_social or approved ACL APIs"
                    ],
                    "configured": bool(
                        scopes.intersection({"w_organization_social", "r_organization_social"})
                    ),
                    "note": (
                        "Organization tools work only for approved app products and admin roles."
                    ),
                },
                "events": {
                    "available_when": ["r_events (read)", "rw_events (create/modify)"],
                    "configured": "r_events" in scopes or "rw_events" in scopes,
                    "note": "Requires Events Management API product and org admin role.",
                },
                "verification": {
                    "available_when": ["r_verify"],
                    "configured": "r_verify" in scopes,
                    "note": "Requires Verified on LinkedIn product.",
                },
                "advanced_api_get": {
                    "available_when": ["any approved /rest or /v2 read endpoint"],
                    "configured": config.has_access_token,
                    "note": "Read-only escape hatch for approved LinkedIn APIs.",
                },
                "advanced_api_post": {
                    "available_when": ["any approved /rest or /v2 write endpoint"],
                    "configured": config.has_access_token,
                    "note": "Write escape hatch for approved LinkedIn APIs.",
                },
            },
        }

    @mcp.tool(tags={"auth"})
    def linkedin_validate_credentials() -> dict[str, Any]:
        """Validate that required LinkedIn environment variables are present."""
        config = load_config()
        return {
            "ok": True,
            "has_client_id": bool(config.client_id),
            "has_client_secret": bool(config.client_secret),
            "redirect_uri": config.redirect_uri,
            "has_access_token": config.has_access_token,
            "has_member_urn_override": bool(config.member_urn),
            "token_file": str(default_token_file()),
            "scopes": list(config.scopes),
            "api_version": config.api_version,
        }

    @mcp.tool(tags={"auth"})
    def linkedin_set_member_urn(member_urn: str) -> dict[str, Any]:
        """Store the authenticated member URN used as the author for personal posts."""
        try:
            token_file = save_member_urn(member_urn)
            return {"ok": True, "member_urn": member_urn.strip(), "token_file": str(token_file)}
        except ValueError as error:
            return {"ok": False, "error": "validation_error", "message": str(error)}
