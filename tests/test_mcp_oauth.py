import pytest

from linkedin_fastmcp.mcp_oauth import (
    create_state,
    exchange_code,
    get_linkedin_token,
    resolve_callback,
    revoke,
)


def test_full_oauth_flow():
    """Test the complete MCP OAuth lifecycle: state -> callback -> exchange -> lookup."""
    # 1. Client initiates authorization
    state, linkedin_state = create_state("http://localhost:3000/callback")
    assert state == linkedin_state
    assert len(state) > 20

    # 2. LinkedIn redirects back, server resolves callback
    mcp_code, redirect_uri = resolve_callback(state, "linkedin-access-token-abc")
    assert redirect_uri == "http://localhost:3000/callback"
    assert len(mcp_code) > 20

    # 3. Client exchanges MCP code for MCP bearer token
    mcp_token = exchange_code(mcp_code)
    assert len(mcp_token) > 20

    # 4. Server can look up LinkedIn token from MCP token
    linkedin_token = get_linkedin_token(mcp_token)
    assert linkedin_token == "linkedin-access-token-abc"


def test_resolve_callback_unknown_state():
    with pytest.raises(ValueError, match="Unknown or expired"):
        resolve_callback("nonexistent-state", "token")


def test_exchange_code_invalid():
    with pytest.raises(ValueError, match="Invalid or expired"):
        exchange_code("nonexistent-code")


def test_state_is_single_use():
    state, _ = create_state("http://localhost/cb")
    resolve_callback(state, "token")
    with pytest.raises(ValueError):
        resolve_callback(state, "token")


def test_code_is_single_use():
    state, _ = create_state("http://localhost/cb")
    code, _ = resolve_callback(state, "token")
    exchange_code(code)
    with pytest.raises(ValueError):
        exchange_code(code)


def test_revoke_session():
    state, _ = create_state("http://localhost/cb")
    code, _ = resolve_callback(state, "my-token")
    mcp_token = exchange_code(code)

    assert get_linkedin_token(mcp_token) == "my-token"
    assert revoke(mcp_token) is True
    assert get_linkedin_token(mcp_token) is None
    assert revoke(mcp_token) is False


def test_get_linkedin_token_unknown():
    assert get_linkedin_token("nonexistent") is None
