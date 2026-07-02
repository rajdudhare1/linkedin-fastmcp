from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import LinkPostInput, TextPostInput, Visibility


def register_post_tools(mcp: FastMCP) -> None:
    @mcp.tool(annotations={"destructiveHint": True}, tags={"posts"})
    async def linkedin_create_text_post(
        text: str,
        visibility: Visibility = Visibility.public,
    ) -> dict[str, Any]:
        """Create a text post on the authenticated member's personal LinkedIn profile."""
        try:
            payload = TextPostInput(text=text, visibility=visibility)
            result = await LinkedInClient(load_config()).create_text_post(payload)
            return {"ok": True, "post": result}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"posts"})
    async def linkedin_create_link_post(
        text: str,
        url: str,
        title: str | None = None,
        description: str | None = None,
        visibility: Visibility = Visibility.public,
    ) -> dict[str, Any]:
        """Create a link post on the authenticated member's personal LinkedIn profile."""
        try:
            payload = LinkPostInput(
                text=text,
                url=url,
                title=title,
                description=description,
                visibility=visibility,
            )
            result = await LinkedInClient(load_config()).create_link_post(payload)
            return {"ok": True, "post": result}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"posts"})
    async def linkedin_get_post(post_urn: str) -> dict[str, Any]:
        """Get a LinkedIn post by URN where LinkedIn API permissions allow it."""
        try:
            if not post_urn.strip():
                return {"ok": False, "error": "validation_error", "message": "post_urn is required"}
            post = await LinkedInClient(load_config()).get_post(post_urn.strip())
            return {"ok": True, "post": post}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"posts"})
    async def linkedin_list_posts(count: int = 10, start: int = 0) -> dict[str, Any]:
        """List posts authored by the authenticated member."""
        try:
            client = LinkedInClient(load_config())
            author_urn = await client._author_urn()
            posts = await client.list_posts(
                author_urn,
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "author_urn": author_urn, "posts": posts}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"posts"})
    async def linkedin_delete_post(post_urn: str) -> dict[str, Any]:
        """Delete a LinkedIn post by URN."""
        try:
            if not post_urn.strip():
                return {"ok": False, "error": "validation_error", "message": "post_urn is required"}
            result = await LinkedInClient(load_config()).delete_post(post_urn.strip())
            return {"ok": True, "post_urn": post_urn.strip(), "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
