import pytest

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInConfigError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import LinkPostInput, TextPostInput


def config() -> LinkedInConfig:
    return LinkedInConfig(
        client_id="client-id",
        client_secret="secret",
        redirect_uri="http://localhost:8000/callback",
        access_token="token",
        member_urn=None,
        scopes=("r_profile_basicinfo", "w_member_social"),
        api_version="202602",
    )


@pytest.mark.anyio
async def test_get_me_falls_back_to_basic_profile(monkeypatch):
    client = LinkedInClient(config())

    async def fake_get_userinfo():
        raise LinkedInAPIError(403, "denied")

    async def fake_get_basic_profile():
        return {"id": "person-id"}

    monkeypatch.setattr(client, "get_userinfo", fake_get_userinfo)
    monkeypatch.setattr(client, "get_basic_profile", fake_get_basic_profile)

    assert await client.get_me() == {"id": "person-id"}


@pytest.mark.anyio
async def test_author_urn_uses_basic_profile_id(monkeypatch):
    client = LinkedInClient(config())

    async def fake_get_me():
        return {"id": "person-id"}

    monkeypatch.setattr(client, "get_me", fake_get_me)

    assert await client._author_urn() == "urn:li:person:person-id"


@pytest.mark.anyio
async def test_author_urn_normalizes_member_urn():
    client = LinkedInClient(
        LinkedInConfig(
            client_id="client-id",
            client_secret="secret",
            redirect_uri="http://localhost:8000/callback",
            access_token="token",
            member_urn="urn:li:member:73912535",
            scopes=("r_profile_basicinfo", "w_member_social"),
            api_version="202602",
        )
    )

    assert await client._author_urn() == "urn:li:person:73912535"


@pytest.mark.anyio
async def test_list_posts_uses_author_query(monkeypatch):
    client = LinkedInClient(config())

    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = kwargs.get("params")
        return {"elements": []}

    monkeypatch.setattr(client, "_request", fake_request)

    await client.list_posts("urn:li:person:73912535", count=5, start=2)

    assert captured["method"] == "GET"
    assert captured["path"] == "/rest/posts"
    assert captured["params"] == {
        "q": "author",
        "author": "urn:li:person:73912535",
        "count": 5,
        "start": 2,
        "sortBy": "LAST_MODIFIED",
    }


@pytest.mark.anyio
async def test_like_activity_uses_actor_path(monkeypatch):
    client = LinkedInClient(config())
    captured = {}

    async def fake_author_urn():
        return "urn:li:person:person-id"

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        return {"status_code": 204}

    monkeypatch.setattr(client, "_author_urn", fake_author_urn)
    monkeypatch.setattr(client, "_request", fake_request)

    await client.like_activity("urn:li:activity:123")

    assert captured["method"] == "PUT"
    assert captured["path"] == (
        "/rest/socialActions/urn%3Ali%3Aactivity%3A123/likes/urn%3Ali%3Aperson%3Aperson-id"
    )


@pytest.mark.anyio
async def test_create_repost_payload(monkeypatch):
    client = LinkedInClient(config())
    captured = {}

    async def fake_author_urn():
        return "urn:li:person:person-id"

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = kwargs.get("json")
        return {"id": "urn:li:share:1"}

    monkeypatch.setattr(client, "_author_urn", fake_author_urn)
    monkeypatch.setattr(client, "_request", fake_request)

    await client.create_repost("urn:li:share:source", commentary="Good read")

    assert captured["method"] == "POST"
    assert captured["path"] == "/rest/posts"
    assert captured["json"]["author"] == "urn:li:person:person-id"
    assert captured["json"]["commentary"] == "Good read"
    assert captured["json"]["content"] == {"post": "urn:li:share:source"}


@pytest.mark.anyio
async def test_organization_text_post_uses_organization_author(monkeypatch):
    client = LinkedInClient(config())
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = kwargs.get("json")
        return {"id": "urn:li:share:1"}

    monkeypatch.setattr(client, "_request", fake_request)

    await client.create_organization_text_post(
        "urn:li:organization:123",
        TextPostInput(text="hello"),
    )

    assert captured["method"] == "POST"
    assert captured["path"] == "/rest/posts"
    assert captured["json"]["author"] == "urn:li:organization:123"
    assert captured["json"]["commentary"] == "hello"


@pytest.mark.anyio
async def test_organization_link_post_uses_organization_author(monkeypatch):
    client = LinkedInClient(config())
    captured = {}

    async def fake_request(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = kwargs.get("json")
        return {"id": "urn:li:share:1"}

    monkeypatch.setattr(client, "_request", fake_request)

    await client.create_organization_link_post(
        "123",
        LinkPostInput(text="hello", url="https://example.com"),
    )

    assert captured["method"] == "POST"
    assert captured["path"] == "/rest/posts"
    assert captured["json"]["author"] == "urn:li:organization:123"
    assert captured["json"]["content"]["article"]["source"] == "https://example.com/"


@pytest.mark.anyio
async def test_api_get_restricts_paths(monkeypatch):
    client = LinkedInClient(config())

    async def fake_request(method, path, **kwargs):
        return {"method": method, "path": path, "params": kwargs.get("params")}

    monkeypatch.setattr(client, "_request", fake_request)

    result = await client.api_get("rest/posts", params={"count": 1})

    assert result == {"method": "GET", "path": "/rest/posts", "params": {"count": 1}}

    with pytest.raises(LinkedInConfigError):
        await client.api_get("https://api.linkedin.com/rest/posts")


@pytest.mark.anyio
async def test_api_post_sends_json(monkeypatch):
    client = LinkedInClient(config())

    async def fake_request(method, path, **kwargs):
        return {"method": method, "path": path, "json": kwargs.get("json")}

    monkeypatch.setattr(client, "_request", fake_request)

    body = {"commentary": "hello", "visibility": "PUBLIC"}
    result = await client.api_post("/rest/posts", json=body)

    assert result == {"method": "POST", "path": "/rest/posts", "json": body}

    with pytest.raises(LinkedInConfigError):
        await client.api_post("https://evil.com/steal")
