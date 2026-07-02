import pytest
from pydantic import ValidationError

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import ImagePostInput, Visibility


def _config() -> LinkedInConfig:
    return LinkedInConfig(
        client_id="client-id",
        client_secret="secret",
        redirect_uri="http://localhost:8000/callback",
        access_token="token",
        member_urn="urn:li:person:test-user",
        scopes=("w_member_social",),
        api_version="202602",
    )


@pytest.mark.anyio
async def test_register_image_upload(monkeypatch):
    client = LinkedInClient(_config())
    captured = {}

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = json
        captured["restli"] = restli
        return {
            "value": {
                "uploadMechanism": {
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                        "uploadUrl": "https://api.linkedin.com/mediaUpload/xyz",
                    }
                },
                "asset": "urn:li:digitalmediaAsset:C55xyz",
            }
        }

    monkeypatch.setattr(client, "_request", fake_request)
    result = await client.register_image_upload()

    assert captured["method"] == "POST"
    assert "registerUpload" in captured["path"]
    assert captured["restli"] is False
    upload_req = captured["json"]["registerUploadRequest"]
    assert upload_req["owner"] == "urn:li:person:test-user"
    assert result["value"]["asset"] == "urn:li:digitalmediaAsset:C55xyz"


@pytest.mark.anyio
async def test_register_image_upload_custom_owner(monkeypatch):
    client = LinkedInClient(_config())

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        return {"value": {"asset": "urn:li:digitalmediaAsset:abc"}}

    monkeypatch.setattr(client, "_request", fake_request)
    result = await client.register_image_upload("urn:li:organization:999")
    assert result["value"]["asset"] == "urn:li:digitalmediaAsset:abc"


@pytest.mark.anyio
async def test_create_image_post(monkeypatch):
    client = LinkedInClient(_config())
    captured = {}

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        captured["method"] = method
        captured["path"] = path
        captured["json"] = json
        return {"id": "urn:li:share:123", "status_code": 201}

    monkeypatch.setattr(client, "_request", fake_request)

    post = ImagePostInput(
        text="Check out this image!",
        image_urn="urn:li:digitalmediaAsset:C55xyz",
        image_title="My Photo",
        image_alt_text="A scenic view",
        visibility=Visibility.public,
    )
    result = await client.create_image_post(post)

    assert captured["method"] == "POST"
    assert captured["path"] == "/rest/posts"
    assert captured["json"]["author"] == "urn:li:person:test-user"
    assert captured["json"]["commentary"] == "Check out this image!"
    assert captured["json"]["content"]["media"]["id"] == "urn:li:digitalmediaAsset:C55xyz"
    assert captured["json"]["content"]["media"]["title"] == "My Photo"
    assert captured["json"]["content"]["media"]["altText"] == "A scenic view"
    assert result["id"] == "urn:li:share:123"


def test_image_post_input_validation():
    with pytest.raises(ValidationError):
        ImagePostInput(text="hello", image_urn="")

    with pytest.raises(ValidationError):
        ImagePostInput(text="", image_urn="urn:li:digitalmediaAsset:abc")

    valid = ImagePostInput(text="hello", image_urn="urn:li:digitalmediaAsset:abc")
    assert valid.image_urn == "urn:li:digitalmediaAsset:abc"
    assert valid.image_title is None
    assert valid.image_alt_text is None


@pytest.mark.anyio
async def test_upload_image_calls_post(monkeypatch):
    import httpx

    client = LinkedInClient(_config())
    captured = {}

    class FakeResponse:
        status_code = 201
        is_error = False

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def post(self, url, *, content, headers):
            captured["url"] = url
            captured["content_len"] = len(content)
            captured["auth_header"] = headers.get("Authorization")
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: FakeClient())
    status = await client.upload_image("https://api.linkedin.com/mediaUpload/xyz", b"\x89PNG")

    assert status == 201
    assert captured["url"] == "https://api.linkedin.com/mediaUpload/xyz"
    assert captured["content_len"] == 4
    assert captured["auth_header"] == "Bearer token"
