from __future__ import annotations

import base64
from typing import Any

from fastmcp import FastMCP
from pydantic import ValidationError

from linkedin_fastmcp.config import load_config
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInFastMCPError
from linkedin_fastmcp.linkedin_client import LinkedInClient
from linkedin_fastmcp.schemas import ImagePostInput, Visibility


def register_media_tools(mcp: FastMCP) -> None:
    @mcp.tool(tags={"media"})
    async def linkedin_register_image_upload(
        owner_urn: str | None = None,
    ) -> dict[str, Any]:
        """Register an image upload with LinkedIn (w_member_social).

        Returns an upload URL and asset URN. Use the upload URL with
        linkedin_upload_image, then pass the asset URN to linkedin_create_image_post.

        Args:
            owner_urn: Optional owner URN. Defaults to the authenticated member.
        """
        try:
            result = await LinkedInClient(load_config()).register_image_upload(owner_urn)
            upload_url = (
                result.get("value", {})
                .get("uploadMechanism", {})
                .get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
                .get("uploadUrl")
            )
            asset = result.get("value", {}).get("asset")
            return {
                "ok": True,
                "upload_url": upload_url,
                "asset": asset,
                "raw": result,
            }
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"media"})
    async def linkedin_upload_image(
        upload_url: str,
        image_base64: str,
    ) -> dict[str, Any]:
        """Upload image binary data to the URL obtained from linkedin_register_image_upload.

        The image must be provided as a base64-encoded string. After a
        successful upload, use the asset URN from the registration step with
        linkedin_create_image_post.

        Args:
            upload_url: The upload URL returned by linkedin_register_image_upload.
            image_base64: Base64-encoded image data (PNG, JPG, or GIF).
        """
        try:
            if not upload_url.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "upload_url is required",
                }
            if not image_base64.strip():
                return {
                    "ok": False,
                    "error": "validation_error",
                    "message": "image_base64 is required",
                }
            image_data = base64.b64decode(image_base64)
            status = await LinkedInClient(load_config()).upload_image(
                upload_url.strip(), image_data
            )
            return {"ok": True, "status_code": status}
        except Exception as exc:
            if isinstance(exc, LinkedInAPIError):
                return exc.as_dict()
            return {"ok": False, "error": type(exc).__name__, "message": str(exc)}

    @mcp.tool(annotations={"destructiveHint": True}, tags={"media", "posts"})
    async def linkedin_create_image_post(
        text: str,
        image_urn: str,
        image_title: str | None = None,
        image_description: str | None = None,
        image_alt_text: str | None = None,
        visibility: Visibility = Visibility.public,
    ) -> dict[str, Any]:
        """Create a post with an already-uploaded image on the member's profile.

        Full workflow:
        1. linkedin_register_image_upload -> gives upload_url + asset URN
        2. linkedin_upload_image(upload_url, base64_data) -> uploads the binary
        3. linkedin_create_image_post(text, asset_urn) -> creates the post

        Args:
            text: Post body text (1-3000 chars).
            image_urn: The asset URN returned from register (urn:li:digitalmediaAsset:...).
            image_title: Optional title overlay for the image.
            image_description: Optional description for the image.
            image_alt_text: Optional alt text for accessibility.
            visibility: PUBLIC or CONNECTIONS.
        """
        try:
            payload = ImagePostInput(
                text=text,
                image_urn=image_urn,
                image_title=image_title,
                image_description=image_description,
                image_alt_text=image_alt_text,
                visibility=visibility,
            )
            result = await LinkedInClient(load_config()).create_image_post(payload)
            return {"ok": True, "post": result}
        except ValidationError as error:
            return {"ok": False, "error": "validation_error", "details": error.errors()}
        except LinkedInAPIError as error:
            return error.as_dict()
        except LinkedInFastMCPError as error:
            return {"ok": False, "error": type(error).__name__, "message": str(error)}
