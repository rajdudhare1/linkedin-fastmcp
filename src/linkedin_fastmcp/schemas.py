from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Visibility(StrEnum):
    public = "PUBLIC"
    connections = "CONNECTIONS"


class TextPostInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=3000)
    visibility: Visibility = Visibility.public

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Post text must not be blank")
        return value


class LinkPostInput(TextPostInput):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=400)
    description: str | None = Field(default=None, max_length=800)


class CommentInput(BaseModel):
    activity_urn: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1, max_length=1250)

    @field_validator("activity_urn", "text")
    @classmethod
    def must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


class RepostInput(BaseModel):
    post_urn: str = Field(..., min_length=1)
    commentary: str | None = Field(default=None, max_length=3000)
    visibility: Visibility = Visibility.public

    @field_validator("post_urn")
    @classmethod
    def post_urn_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("post_urn is required")
        return value

    @field_validator("commentary")
    @classmethod
    def commentary_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class EventType(StrEnum):
    in_person = "IN_PERSON"
    external = "EXTERNAL"


class EventInput(BaseModel):
    organization_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    event_type: EventType = EventType.external
    start_at: int = Field(..., description="Start epoch ms")
    end_at: int = Field(..., description="End epoch ms")
    event_url: HttpUrl | None = None

    @field_validator("organization_id", "name")
    @classmethod
    def must_not_be_blank_ev(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value must not be blank")
        return value


# ---------------------------------------------------------------------------
# Media / Image upload
# ---------------------------------------------------------------------------

class ImagePostInput(TextPostInput):
    """Post with an already-uploaded image asset URN."""

    image_urn: str = Field(..., min_length=1)
    image_title: str | None = Field(default=None, max_length=400)
    image_description: str | None = Field(default=None, max_length=800)
    image_alt_text: str | None = Field(default=None, max_length=4086)

    @field_validator("image_urn")
    @classmethod
    def image_urn_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("image_urn is required")
        return value
