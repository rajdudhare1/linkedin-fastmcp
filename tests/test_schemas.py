import pytest
from pydantic import ValidationError

from linkedin_fastmcp.schemas import CommentInput, LinkPostInput, RepostInput, TextPostInput


def test_text_post_strips_text():
    post = TextPostInput(text="  hello LinkedIn  ")

    assert post.text == "hello LinkedIn"


def test_text_post_rejects_blank_text():
    with pytest.raises(ValidationError):
        TextPostInput(text="   ")


def test_link_post_accepts_url():
    post = LinkPostInput(text="Read this", url="https://example.com/article")

    assert str(post.url) == "https://example.com/article"


def test_comment_rejects_blank_text():
    with pytest.raises(ValidationError):
        CommentInput(activity_urn="urn:li:activity:123", text="")


def test_repost_strips_optional_commentary():
    repost = RepostInput(post_urn=" urn:li:share:123 ", commentary="  worth reading  ")

    assert repost.post_urn == "urn:li:share:123"
    assert repost.commentary == "worth reading"
