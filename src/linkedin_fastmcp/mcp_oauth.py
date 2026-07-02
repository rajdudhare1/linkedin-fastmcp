"""MCP-level OAuth provider that proxies to LinkedIn OAuth.

OpenCode (or any MCP client) talks to *this* OAuth server. The authorize
endpoint redirects to LinkedIn. On callback, the LinkedIn access token is
stored and an MCP-level authorization code is issued. The /token endpoint
exchanges that code for an MCP bearer token that maps 1-to-1 to the
LinkedIn session.

This avoids the need for in-LLM auth tools -- OpenCode handles the
browser flow natively.
"""

from __future__ import annotations

import secrets
from collections import OrderedDict
from dataclasses import dataclass

_MAX_ENTRIES = 1000

class _BoundedDict(OrderedDict):
    """OrderedDict that evicts oldest entries when capacity is exceeded."""
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        while len(self) > _MAX_ENTRIES:
            self.popitem(last=False)

# Pending authorization states keyed by ``state`` value.
_pending_states: _BoundedDict = _BoundedDict()

# Issued authorization codes keyed by code value.
_auth_codes: _BoundedDict = _BoundedDict()  # code -> linkedin_access_token

# Active MCP sessions keyed by bearer token.
_sessions: _BoundedDict = _BoundedDict()  # mcp_token -> linkedin_access_token


@dataclass
class _PendingAuth:
    """Tracks a single in-flight OAuth authorization."""

    state: str
    redirect_uri: str  # MCP client's redirect_uri


def create_state(redirect_uri: str) -> tuple[str, str]:
    """Create a new pending authorization and return (state, linkedin_state).

    ``state`` is the LinkedIn-side state value; ``redirect_uri`` is where
    the MCP client wants the code delivered after LinkedIn approval.
    """
    state = secrets.token_urlsafe(32)
    _pending_states[state] = _PendingAuth(state=state, redirect_uri=redirect_uri)
    return state, state


def resolve_callback(state: str, linkedin_access_token: str) -> tuple[str, str]:
    """Called when LinkedIn redirects back with a valid token.

    Returns ``(mcp_auth_code, client_redirect_uri)`` so the server can
    redirect the browser to the MCP client's callback with the code.
    """
    pending = _pending_states.pop(state, None)
    if pending is None:
        raise ValueError("Unknown or expired OAuth state")

    code = secrets.token_urlsafe(48)
    _auth_codes[code] = linkedin_access_token
    return code, pending.redirect_uri


def exchange_code(code: str) -> str:
    """Exchange an MCP authorization code for a bearer token.

    Returns the MCP bearer token.
    """
    linkedin_token = _auth_codes.pop(code, None)
    if linkedin_token is None:
        raise ValueError("Invalid or expired authorization code")

    mcp_token = secrets.token_urlsafe(48)
    _sessions[mcp_token] = linkedin_token
    return mcp_token


def get_linkedin_token(mcp_token: str) -> str | None:
    """Look up the LinkedIn access token for a given MCP bearer token."""
    return _sessions.get(mcp_token)


def revoke(mcp_token: str) -> bool:
    """Revoke an MCP session. Returns True if it existed."""
    return _sessions.pop(mcp_token, None) is not None
