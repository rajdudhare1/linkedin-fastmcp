from __future__ import annotations

import secrets
from typing import Any
from urllib.parse import urlencode

import httpx

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInConfigError

AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


def build_authorization_url(config: LinkedInConfig, *, state: str | None = None) -> dict[str, str]:
    if not config.client_id:
        raise LinkedInConfigError("LINKEDIN_CLIENT_ID is required to build an authorization URL")

    state_value = state or secrets.token_urlsafe(24)
    query = urlencode(
        {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scopes),
            "state": state_value,
        }
    )
    return {"authorization_url": f"{AUTHORIZATION_URL}?{query}", "state": state_value}


async def exchange_code_for_token(config: LinkedInConfig, code: str) -> dict[str, Any]:
    if not config.has_oauth_app:
        raise LinkedInConfigError(
            "LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, and LINKEDIN_REDIRECT_URI are required"
        )
    if not code.strip():
        raise LinkedInConfigError("Authorization code must not be empty")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.redirect_uri,
        "client_id": config.client_id,
        "client_secret": config.client_secret,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(TOKEN_URL, data=data)

    if response.is_error:
        raise LinkedInAPIError(
            response.status_code,
            "LinkedIn token exchange failed",
            _safe_json(response),
        )
    return response.json()


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text
