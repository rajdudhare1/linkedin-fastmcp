from linkedin_fastmcp.config import DEFAULT_SCOPES, load_config


def test_load_config_defaults(monkeypatch):
    for key in (
        "LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET",
        "LINKEDIN_REDIRECT_URI",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_MEMBER_URN",
        "LINKEDIN_SCOPES",
        "LINKEDIN_API_VERSION",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", "/tmp/linkedin-fastmcp-empty-token.json")

    config = load_config(load_env_file=False)

    assert config.client_id is None
    assert config.redirect_uri == "http://localhost:8000/callback"
    assert config.member_urn is None
    assert config.scopes == DEFAULT_SCOPES
    assert config.api_version == "202602"


def test_load_config_splits_scopes(monkeypatch):
    monkeypatch.setenv("LINKEDIN_SCOPES", "openid,profile email w_member_social")

    config = load_config(load_env_file=False)

    assert config.scopes == ("openid", "profile", "email", "w_member_social")


def test_load_config_api_version(monkeypatch):
    monkeypatch.setenv("LINKEDIN_API_VERSION", "202507")
    config = load_config(load_env_file=False)
    assert config.api_version == "202507"
