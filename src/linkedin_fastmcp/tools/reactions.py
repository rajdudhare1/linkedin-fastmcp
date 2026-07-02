from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import RepostInput


def register_reaction_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"reactions"})
    async def linkedin_get_social_action(activity_urn: str) -> dict[str, Any]:
        """Get social action metadata for a post or activity where permissions allow it."""
        try:
            if not activity_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn is required",
                }
            result = await LinkedInClient(load_config()).get_social_action(activity_urn.strip())
            return {"ok": True, "social_action": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"reactions"})
    async def linkedin_list_likes(
        activity_urn: str,
        count: int = 20,
        start: int = 0,
    ) -> dict[str, Any]:
        """List likes for a LinkedIn activity where API permissions allow it."""
        try:
            if not activity_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn is required",
                }
            likes = await LinkedInClient(load_config()).list_likes(
                activity_urn.strip(),
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "likes": likes}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"reactions"})
    async def linkedin_like_activity(activity_urn: str) -> dict[str, Any]:
        """Like a LinkedIn activity as the authenticated member."""
        try:
            if not activity_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn is required",
                }
            result = await LinkedInClient(load_config()).like_activity(activity_urn.strip())
            return {"ok": True, "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"reactions"})
    async def linkedin_unlike_activity(activity_urn: str) -> dict[str, Any]:
        """Remove the authenticated member's like from a LinkedIn activity."""
        try:
            if not activity_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn is required",
                }
            result = await LinkedInClient(load_config()).unlike_activity(activity_urn.strip())
            return {"ok": True, "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"posts", "reactions"})
    async def linkedin_repost(
        post_urn: str,
        commentary: str | None = None,
        visibility: str = "PUBLIC",
    ) -> dict[str, Any]:
        """Repost a LinkedIn post with optional commentary where permissions allow it."""
        try:
            payload = RepostInput(
                post_urn=post_urn,
                commentary=commentary,
                visibility=visibility,
            )
            repost = await LinkedInClient(load_config()).create_repost(
                payload.post_urn,
                commentary=payload.commentary,
                visibility=payload.visibility,
            )
            return {"ok": True, "post": repost}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
