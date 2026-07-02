from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient


def register_api_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"api", "advanced"})
    async def linkedin_api_get(
        path: str,
        params: dict[str, Any] | None = None,
        restli: bool = True,
    ) -> dict[str, Any]:
        """Run an authorized read-only LinkedIn API GET for approved /rest or /v2 endpoints."""
        try:
            result = await LinkedInClient(load_config()).api_get(
                path,
                params=params,
                restli=restli,
            )
            return {"ok": True, "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"api", "advanced"})
    async def linkedin_api_post(
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        restli: bool = True,
    ) -> dict[str, Any]:
        """Run an authorized LinkedIn API POST for approved /rest or /v2 endpoints.

        Use this as an escape hatch for any write endpoint not covered by
        dedicated tools. The path must start with /rest/ or /v2/.

        Args:
            path: API path (e.g. /rest/posts, /v2/ugcPosts).
            body: JSON request body.
            params: Optional query parameters.
            restli: Include LinkedIn-Version and X-Restli headers (default True).
        """
        try:
            result = await LinkedInClient(load_config()).api_post(
                path,
                json=body,
                params=params,
                restli=restli,
            )
            return {"ok": True, "result": result}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"jobs"})
    async def linkedin_get_job(job_id: str) -> dict[str, Any]:
        """Get a LinkedIn job by ID where the app has API access."""
        try:
            if not job_id.strip():
                return {"ok": False, "error": "validation_error", "message": "job_id is required"}
            job = await LinkedInClient(load_config()).get_job(job_id.strip())
            return {"ok": True, "job": job}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"jobs"})
    async def linkedin_search_jobs(
        keywords: str,
        location: str | None = None,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        """Search LinkedIn jobs where the app has API access."""
        try:
            if not keywords.strip():
                return {"ok": False, "error": "validation_error", "message": "keywords is required"}
            jobs = await LinkedInClient(load_config()).search_jobs(
                keywords=keywords.strip(),
                location=location.strip() if location else None,
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "jobs": jobs}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
