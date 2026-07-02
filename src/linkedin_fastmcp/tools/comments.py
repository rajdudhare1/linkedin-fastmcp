from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import CommentInput


def register_comment_tools(mcp: FastMCP) -> None:
    @mcp.tool(annotations={"destructiveHint": True}, tags={"comments"})
    async def linkedin_create_comment(activity_urn: str, text: str) -> dict[str, Any]:
        """Create a comment on a LinkedIn activity where API permissions allow it."""
        try:
            payload = CommentInput(activity_urn=activity_urn, text=text)
            comment = await LinkedInClient(load_config()).create_comment(
                payload.activity_urn,
                payload.text,
            )
            return {"ok": True, "comment": comment}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"comments"})
    async def linkedin_get_comments(activity_urn: str, count: int = 20) -> dict[str, Any]:
        """Get comments for a LinkedIn activity where API permissions allow it."""
        try:
            if not activity_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn is required",
                }
            count = min(max(count, 1), 100)
            comments = await LinkedInClient(load_config()).get_comments(
                activity_urn.strip(),
                count=count,
            )
            return {"ok": True, "comments": comments}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"comments"})
    async def linkedin_reply_to_comment(
        activity_urn: str,
        parent_comment_urn: str,
        text: str,
    ) -> dict[str, Any]:
        """Reply to a LinkedIn comment."""
        try:
            payload = CommentInput(activity_urn=activity_urn, text=text)
            if not parent_comment_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "parent_comment_urn is required",
                }
            reply = await LinkedInClient(load_config()).create_comment(
                payload.activity_urn,
                payload.text,
                parent_comment_urn=parent_comment_urn.strip(),
            )
            return {"ok": True, "reply": reply}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"comments"})
    async def linkedin_delete_comment(activity_urn: str, comment_urn: str) -> dict[str, Any]:
        """Delete a LinkedIn comment."""
        try:
            if not activity_urn.strip() or not comment_urn.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "activity_urn and comment_urn are required",
                }
            result = await LinkedInClient(load_config()).delete_comment(
                activity_urn.strip(),
                comment_urn.strip(),
            )
            return {"ok": True, "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
