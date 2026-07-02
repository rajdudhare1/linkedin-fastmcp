import pytest
from pydantic import ValidationError

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import EventInput, EventType


def _config() -> LinkedInConfig:
    return LinkedInConfig(
        client_id="client-id",
        client_secret="secret",
        redirect_uri="http://localhost:8000/callback",
        access_token="token",
        member_urn="urn:li:person:test-user",
        scopes=("r_events", "rw_events"),
        api_version="202602",
    )


@pytest.mark.anyio
async def test_list_organization_events(monkeypatch):
    client = LinkedInClient(_config())
    captured = {}

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        return {"elements": []}

    monkeypatch.setattr(client, "_request", fake_request)
    result = await client.list_organization_events("123", count=5, start=0)

    assert captured["method"] == "GET"
    assert captured["path"] == "/rest/events"
    assert captured["params"]["q"] == "eventsByOrganizer"
    assert captured["params"]["organizer"] == "urn:li:organization:123"
    assert result == {"elements": []}


@pytest.mark.anyio
async def test_get_event(monkeypatch):
    client = LinkedInClient(_config())
    captured = {}

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        captured["method"] = method
        captured["path"] = path
        return {"id": "evt-1", "name": "Test Event"}

    monkeypatch.setattr(client, "_request", fake_request)
    result = await client.get_event("evt-1")

    assert captured["method"] == "GET"
    assert "evt-1" in captured["path"]
    assert result["name"] == "Test Event"


@pytest.mark.anyio
async def test_create_event_external(monkeypatch):
    client = LinkedInClient(_config())
    captured = {}

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        captured["method"] = method
        captured["json"] = json
        return {"id": "new-event-id", "status_code": 201}

    monkeypatch.setattr(client, "_request", fake_request)

    event = EventInput(
        organization_id="456",
        name="My Event",
        start_at=1700000000000,
        end_at=1700003600000,
        description="A test event",
        event_type=EventType.external,
        event_url="https://example.com/event",
    )
    result = await client.create_event(event)

    assert captured["method"] == "POST"
    assert captured["json"]["organizer"] == "urn:li:organization:456"
    assert captured["json"]["name"] == "My Event"
    assert "external" in captured["json"]["type"]
    assert result["id"] == "new-event-id"


@pytest.mark.anyio
async def test_create_event_in_person(monkeypatch):
    client = LinkedInClient(_config())

    async def fake_request(method, path, *, json=None, params=None, restli=True):
        return {"id": "ip-event", "status_code": 201}

    monkeypatch.setattr(client, "_request", fake_request)

    event = EventInput(
        organization_id="789",
        name="In-Person Event",
        start_at=1700000000000,
        end_at=1700003600000,
        event_type=EventType.in_person,
    )
    result = await client.create_event(event)
    assert result["id"] == "ip-event"


def test_event_input_validation():
    with pytest.raises(ValidationError):
        EventInput(
            organization_id="",
            name="Test",
            start_at=1700000000000,
            end_at=1700003600000,
        )

    with pytest.raises(ValidationError):
        EventInput(
            organization_id="123",
            name="",
            start_at=1700000000000,
            end_at=1700003600000,
        )
