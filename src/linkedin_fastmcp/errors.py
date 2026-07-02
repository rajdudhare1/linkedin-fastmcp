from __future__ import annotations

from typing import Any


class LinkedInFastMCPError(Exception):
    """Base error for expected LinkedIn FastMCP failures."""


class LinkedInConfigError(LinkedInFastMCPError):
    """Raised when required configuration is missing."""


class LinkedInAPIError(LinkedInFastMCPError):
    def __init__(self, status_code: int, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "error": "linkedin_api_error",
            "status_code": self.status_code,
            "message": str(self),
            "details": self.details,
        }
