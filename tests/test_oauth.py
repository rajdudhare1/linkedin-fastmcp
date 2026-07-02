from urllib.parse import parse_qs, urlparse

import pytest

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.errors import LinkedInConfigError
from linkedin_fastmcp.oauth import build_authorization_url


def test_build_authorization_url():
    config = LinkedInConfig(
        client_id="client-id",
        client_secret="secret",
        redirect_uri="http://localhost:8080/callback",
        access_token=None,
        member_urn=None,
        scopes=("openid", "w_member_social"),
        api_version="202405",
    )

    result = build_authorization_url(config, state="state-123")
    parsed = urlparse(result["authorization_url"])
    params = parse_qs(parsed.query)

    assert parsed.netloc == "www.linkedin.com"
    assert params["response_type"] == ["code"]
    assert params["client_id"] == ["client-id"]
    assert params["redirect_uri"] == ["http://localhost:8080/callback"]
    assert params["scope"] == ["openid w_member_social"]
    assert params["state"] == ["state-123"]
    assert result["state"] == "state-123"


def test_build_authorization_url_requires_client_id():
    config = LinkedInConfig(
        client_id=None,
        client_secret=None,
        redirect_uri="http://localhost:8080/callback",
        access_token=None,
        member_urn=None,
        scopes=("openid",),
        api_version="202405",
    )

    with pytest.raises(LinkedInConfigError):
        build_authorization_url(config)
