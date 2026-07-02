import json

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.token_store import (
    default_token_file,
    load_access_token,
    load_member_urn,
    save_member_urn,
    save_token_response,
)


def test_save_and_load_token(monkeypatch, tmp_path):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))

    saved_to = save_token_response({"access_token": "abc123", "expires_in": 3600})

    assert saved_to == token_file
    assert load_access_token() == "abc123"
    assert json.loads(token_file.read_text())["expires_in"] == 3600


def test_default_token_file_respects_env(monkeypatch, tmp_path):
    token_file = tmp_path / "custom.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))

    assert default_token_file() == token_file


def test_config_uses_token_file_when_env_token_missing(monkeypatch, tmp_path):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    save_token_response({"access_token": "from-file"})

    config = load_config(load_env_file=False)

    assert config.access_token == "from-file"


def test_env_token_wins_over_token_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("LINKEDIN_ACCESS_TOKEN", "from-env")
    save_token_response({"access_token": "from-file"})

    config = load_config(load_env_file=False)

    assert config.access_token == "from-env"


def test_save_and_load_member_urn(monkeypatch, tmp_path):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))

    save_token_response({"access_token": "abc123"})
    save_member_urn("urn:li:member:73912535")

    assert load_member_urn() == "urn:li:member:73912535"


def test_config_uses_member_urn_from_token_file(monkeypatch, tmp_path):
    token_file = tmp_path / "token.json"
    monkeypatch.setenv("LINKEDIN_TOKEN_FILE", str(token_file))
    monkeypatch.delenv("LINKEDIN_MEMBER_URN", raising=False)
    save_token_response({"access_token": "abc123"})
    save_member_urn("urn:li:member:73912535")

    config = load_config(load_env_file=False)

    assert config.member_urn == "urn:li:member:73912535"
