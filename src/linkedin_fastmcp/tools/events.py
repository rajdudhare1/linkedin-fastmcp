from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import EventInput, EventType


def register_event_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"events"})
    async def linkedin_list_organization_events(
        organization_id: str,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        """List events for an organization where the member has admin access (r_events)."""
        try:
            if not organization_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "organization_id is required",
                }
            events = await LinkedInClient(load_config()).list_organization_events(
                organization_id.strip(),
                count=min(max(count, 1), 100),
                start=max(start, 0),
            )
            return {"ok": True, "events": events}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(tags={"events"})
    async def linkedin_get_event(event_id: str) -> dict[str, Any]:
        """Get a LinkedIn event by its ID (r_events)."""
        try:
            if not event_id.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "event_id is required",
                }
            event = await LinkedInClient(load_config()).get_event(event_id.strip())
            return {"ok": True, "event": event}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"events"})
    async def linkedin_create_event(
        organization_id: str,
        name: str,
        start_at: int,
        end_at: int,
        description: str | None = None,
        event_type: EventType = EventType.external,
        event_url: str | None = None,
    ) -> dict[str, Any]:
        """Create an organization event on LinkedIn (rw_events).

        Args:
            organization_id: Numeric org ID or urn:li:organization:...
            name: Event name.
            start_at: Start time as epoch milliseconds.
            end_at: End time as epoch milliseconds.
            description: Optional event description.
            event_type: IN_PERSON or EXTERNAL (default EXTERNAL).
            event_url: URL for external events.
        """
        try:
            payload = EventInput(
                organization_id=organization_id,
                name=name,
                start_at=start_at,
                end_at=end_at,
                description=description,
                event_type=event_type,
                event_url=event_url,
            )
            result = await LinkedInClient(load_config()).create_event(payload)
            return {"ok": True, "event": result}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
