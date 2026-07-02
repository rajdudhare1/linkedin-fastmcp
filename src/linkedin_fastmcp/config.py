from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from linkedin_fastmcp.token_store import load_access_token, load_member_urn

DEFAULT_SCOPES = (
    "openid",
    "profile",
    "email",
    "r_profile_basicinfo",
    "w_member_social",
    "r_events",
    "rw_events",
)


@dataclass(frozen=True)
class LinkedInConfig:
    client_id: str | None
    client_secret: str | None
    redirect_uri: str
    access_token: str | None
    member_urn: str | None
    scopes: tuple[str, ...]
    api_version: str

    @property
    def has_oauth_app(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    @property
    def has_access_token(self) -> bool:
        return bool(self.access_token)


def _split_scopes(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_SCOPES
    return tuple(scope for scope in value.replace(",", " ").split() if scope)


def load_config(*, load_env_file: bool = True) -> LinkedInConfig:
    if load_env_file:
        load_dotenv()
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN") or load_access_token()
    member_urn = os.getenv("LINKEDIN_MEMBER_URN") or load_member_urn()
    return LinkedInConfig(
        client_id=os.getenv("LINKEDIN_CLIENT_ID"),
        client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
        redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"),
        access_token=access_token,
        member_urn=member_urn,
        scopes=_split_scopes(os.getenv("LINKEDIN_SCOPES")),
        api_version=os.getenv("LINKEDIN_API_VERSION", "202602"),
    )
