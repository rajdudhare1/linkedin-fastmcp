from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient


def register_profile_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"profile"})
    async def linkedin_get_me() -> dict[str, Any]:
        """Get the authenticated member's OpenID Connect profile.

        Uses the /v2/userinfo endpoint (openid scope), falling back to
        /v2/me (r_profile_basicinfo) if userinfo returns 403.
        """
        try:
            return {"ok": True, "profile": await LinkedInClient(load_config()).get_me()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"profile"})
    async def linkedin_get_basic_profile() -> dict[str, Any]:
        """Get the authenticated member's basic profile via /v2/me (r_profile_basicinfo).

        Returns name, headline, profile photo, vanity name, and profile URL.
        """
        try:
            profile = await LinkedInClient(load_config()).get_basic_profile()
            return {"ok": True, "profile": profile}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"profile"})
    async def linkedin_get_email() -> dict[str, Any]:
        """Get the authenticated member's primary email address (email scope).

        Uses the /v2/userinfo endpoint which returns the email when the
        'email' scope was granted during OAuth.
        """
        try:
            userinfo = await LinkedInClient(load_config()).get_userinfo()
            email = userinfo.get("email")
            email_verified = userinfo.get("email_verified")
            return {
                "ok": True,
                "email": email,
                "email_verified": email_verified,
            }
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"profile"})
    async def linkedin_get_verification_status() -> dict[str, Any]:
        """Check the authenticated member's verification status (r_verify).

        Requires the 'Verified on LinkedIn' product enabled in the developer portal.
        """
        try:
            result = await LinkedInClient(load_config()).get_verification_status()
            return {"ok": True, "verification": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
