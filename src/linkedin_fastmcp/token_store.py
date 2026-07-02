from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

TOKEN_FILE_ENV = "LINKEDIN_TOKEN_FILE"


def default_token_file() -> Path:
    configured = os.getenv(TOKEN_FILE_ENV)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "linkedin-fastmcp" / "token.json"


def load_access_token() -> str | None:
    data = load_token_response()
    token = data.get("access_token")
    if isinstance(token, str) and token.strip():
        return token.strip()
    return None


def load_member_urn() -> str | None:
    data = load_token_response()
    member_urn = data.get("member_urn")
    if isinstance(member_urn, str) and member_urn.strip():
        return member_urn.strip()
    return None


def load_token_response() -> dict[str, Any]:
    token_file = default_token_file()
    if not token_file.exists():
        return {}
    try:
        loaded = json.loads(token_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(loaded, dict):
        return loaded
    return {}


def save_token_response(token_response: dict[str, Any]) -> Path:
    access_token = token_response.get("access_token")
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValueError("Token response did not include a non-empty access_token")

    enriched = dict(token_response)
    if "member_urn" not in enriched:
        member_urn = _member_urn_from_id_token(enriched.get("id_token"))
        if member_urn:
            enriched["member_urn"] = member_urn
    return _write_token_response(enriched)


def save_member_urn(member_urn: str) -> Path:
    member_urn = member_urn.strip()
    if not member_urn.startswith("urn:li:"):
        raise ValueError("member_urn must start with 'urn:li:'")
    data = load_token_response()
    data["member_urn"] = member_urn
    return _write_token_response(data)


def _write_token_response(data: dict[str, Any]) -> Path:
    token_file = default_token_file()
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    token_file.chmod(0o600)
    return token_file


def _member_urn_from_id_token(id_token: Any) -> str | None:
    if not isinstance(id_token, str):
        return None
    parts = id_token.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1]
    payload += "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload.encode("ascii"))
        claims = json.loads(decoded.decode("utf-8"))
    except (ValueError, OSError, json.JSONDecodeError):
        return None
    subject = claims.get("sub")
    if isinstance(subject, str) and subject.strip():
        return f"urn:li:person:{subject.strip()}"
    return None
