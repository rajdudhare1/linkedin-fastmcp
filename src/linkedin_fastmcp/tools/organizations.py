from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import LinkPostInput, TextPostInput, Visibility


def register_organization_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"organizations"})
    async def linkedin_list_admin_organizations(count: int = 100, start: int = 0) -> dict[str, Any]:
        """List organizations the authenticated member can administer where allowed."""
        try:
            organizations = await LinkedInClient(load_config()).list_admin_organizations(
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "organizations": organizations}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"organizations"})
    async def linkedin_get_organization(organization_id: str) -> dict[str, Any]:
        """Get an organization by numeric ID or urn:li:organization:... where allowed."""
        try:
            if not organization_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "organization_id is required",
                }
            organization = await LinkedInClient(load_config()).get_organization(
                organization_id.strip()
            )
            return {"ok": True, "organization": organization}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"organizations"})
    async def linkedin_get_organization_by_vanity_name(vanity_name: str) -> dict[str, Any]:
        """Get an organization by LinkedIn vanity name where allowed."""
        try:
            if not vanity_name.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "vanity_name is required",
                }
            organization = await LinkedInClient(load_config()).get_organization_by_vanity_name(
                vanity_name.strip()
            )
            return {"ok": True, "organization": organization}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"organizations", "posts"})
    async def linkedin_create_organization_text_post(
        organization_id: str,
        text: str,
        visibility: Visibility = Visibility.public,
    ) -> dict[str, Any]:
        """Create a text post as an organization/page where the member has permission."""
        try:
            if not organization_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "organization_id is required",
                }
            payload = TextPostInput(text=text, visibility=visibility)
            post = await LinkedInClient(load_config()).create_organization_text_post(
                organization_id.strip(),
                payload,
            )
            return {"ok": True, "post": post}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"organizations", "posts"})
    async def linkedin_create_organization_link_post(
        organization_id: str,
        text: str,
        url: str,
        title: str | None = None,
        description: str | None = None,
        visibility: Visibility = Visibility.public,
    ) -> dict[str, Any]:
        """Create a link post as an organization/page where the member has permission."""
        try:
            if not organization_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "organization_id is required",
                }
            payload = LinkPostInput(
                text=text,
                url=url,
                title=title,
                description=description,
                visibility=visibility,
            )
            post = await LinkedInClient(load_config()).create_organization_link_post(
                organization_id.strip(),
                payload,
            )
            return {"ok": True, "post": post}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"organizations", "posts"})
    async def linkedin_list_organization_posts(
        organization_id: str,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        """List recent posts from an organization's LinkedIn feed."""
        try:
            if not organization_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "organization_id is required",
                }
            posts = await LinkedInClient(load_config()).list_organization_posts(
                organization_id.strip(),
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "posts": posts}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
