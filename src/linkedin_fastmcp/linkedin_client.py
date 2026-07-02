from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from linkedin_fastmcp.config import LinkedInConfig
from linkedin_fastmcp.errors import LinkedInAPIError, LinkedInConfigError
from linkedin_fastmcp.schemas import EventInput, ImagePostInput, LinkPostInput, TextPostInput

API_BASE = "https://api.linkedin.com"


class LinkedInClient:
    def __init__(self, config: LinkedInConfig) -> None:
        if not config.access_token:
            raise LinkedInConfigError("LINKEDIN_ACCESS_TOKEN is required for LinkedIn API calls")
        self.config = config

    async def get_userinfo(self) -> dict[str, Any]:
        return await self._request("GET", "/v2/userinfo", restli=False)

    async def get_basic_profile(self) -> dict[str, Any]:
        return await self._request("GET", "/v2/me")

    async def get_me(self) -> dict[str, Any]:
        try:
            return await self.get_userinfo()
        except LinkedInAPIError as exc:
            if exc.status_code != 403:
                raise
            return await self.get_basic_profile()

    async def get_verification_status(self) -> dict[str, Any]:
        author = await self._author_urn()
        encoded = quote(author, safe="")
        return await self._request("GET", f"/rest/memberVerifications/{encoded}")

    async def create_text_post(self, post: TextPostInput) -> dict[str, Any]:
        author = await self._author_urn()
        payload = {
            "author": author,
            "commentary": post.text,
            "visibility": post.visibility.value,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        return await self._request("POST", "/rest/posts", json=payload)

    async def create_link_post(self, post: LinkPostInput) -> dict[str, Any]:
        author = await self._author_urn()
        return await self._create_link_post(author, post)

    async def create_repost(
        self,
        post_urn: str,
        *,
        commentary: str | None = None,
        visibility: str = "PUBLIC",
    ) -> dict[str, Any]:
        author = await self._author_urn()
        payload: dict[str, Any] = {
            "author": author,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {"post": post_urn},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if commentary:
            payload["commentary"] = commentary
        return await self._request("POST", "/rest/posts", json=payload)

    async def create_organization_text_post(
        self,
        organization_id: str,
        post: TextPostInput,
    ) -> dict[str, Any]:
        author = _organization_urn(organization_id)
        payload = {
            "author": author,
            "commentary": post.text,
            "visibility": post.visibility.value,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        return await self._request("POST", "/rest/posts", json=payload)

    async def create_organization_link_post(
        self,
        organization_id: str,
        post: LinkPostInput,
    ) -> dict[str, Any]:
        return await self._create_link_post(_organization_urn(organization_id), post)

    async def _create_link_post(self, author: str, post: LinkPostInput) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "author": author,
            "commentary": post.text,
            "visibility": post.visibility.value,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "article": {
                    "source": str(post.url),
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        article = payload["content"]["article"]
        if post.title:
            article["title"] = post.title
        if post.description:
            article["description"] = post.description
        return await self._request("POST", "/rest/posts", json=payload)

    async def list_posts(
        self,
        author_urn: str,
        *,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/rest/posts",
            params={
                "q": "author",
                "author": author_urn,
                "count": count,
                "start": start,
                "sortBy": "LAST_MODIFIED",
            },
        )

    async def get_post(self, post_urn: str) -> dict[str, Any]:
        encoded = quote(post_urn, safe="")
        return await self._request("GET", f"/rest/posts/{encoded}")

    async def delete_post(self, post_urn: str) -> dict[str, Any]:
        encoded = quote(post_urn, safe="")
        return await self._request("DELETE", f"/rest/posts/{encoded}")

    async def create_comment(
        self,
        activity_urn: str,
        text: str,
        *,
        parent_comment_urn: str | None = None,
    ) -> dict[str, Any]:
        actor = await self._author_urn()
        payload: dict[str, Any] = {"actor": actor, "message": {"text": text}}
        if parent_comment_urn:
            payload["parentComment"] = parent_comment_urn
        encoded = quote(activity_urn, safe="")
        return await self._request(
            "POST",
            f"/rest/socialActions/{encoded}/comments",
            json=payload,
        )

    async def get_comments(
        self,
        activity_urn: str,
        *,
        count: int = 20,
        start: int = 0,
    ) -> dict[str, Any]:
        encoded = quote(activity_urn, safe="")
        return await self._request(
            "GET",
            f"/rest/socialActions/{encoded}/comments",
            params={"count": count, "start": start},
        )

    async def delete_comment(self, activity_urn: str, comment_urn: str) -> dict[str, Any]:
        actor = await self._author_urn()
        encoded_activity = quote(activity_urn, safe="")
        encoded_comment = quote(comment_urn, safe="")
        return await self._request(
            "DELETE",
            f"/v2/socialActions/{encoded_activity}/comments/{encoded_comment}",
            params={"actor": actor},
            restli=False,
        )

    async def get_social_action(self, activity_urn: str) -> dict[str, Any]:
        encoded = quote(activity_urn, safe="")
        return await self._request("GET", f"/rest/socialActions/{encoded}")

    async def list_likes(
        self,
        activity_urn: str,
        *,
        count: int = 20,
        start: int = 0,
    ) -> dict[str, Any]:
        encoded = quote(activity_urn, safe="")
        return await self._request(
            "GET",
            f"/rest/socialActions/{encoded}/likes",
            params={"count": count, "start": start},
        )

    async def like_activity(self, activity_urn: str) -> dict[str, Any]:
        actor = await self._author_urn()
        encoded_activity = quote(activity_urn, safe="")
        encoded_actor = quote(actor, safe="")
        return await self._request(
            "PUT",
            f"/rest/socialActions/{encoded_activity}/likes/{encoded_actor}",
        )

    async def unlike_activity(self, activity_urn: str) -> dict[str, Any]:
        actor = await self._author_urn()
        encoded_activity = quote(activity_urn, safe="")
        encoded_actor = quote(actor, safe="")
        return await self._request(
            "DELETE",
            f"/rest/socialActions/{encoded_activity}/likes/{encoded_actor}",
        )

    async def list_admin_organizations(self, *, count: int = 100, start: int = 0) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/rest/organizationAcls",
            params={
                "q": "roleAssignee",
                "roleAssignee": await self._author_urn(),
                "role": "ADMINISTRATOR",
                "state": "APPROVED",
                "count": count,
                "start": start,
            },
        )

    async def get_organization(self, organization_id: str) -> dict[str, Any]:
        encoded = quote(_organization_id(organization_id), safe="")
        return await self._request("GET", f"/rest/organizations/{encoded}")

    async def get_organization_by_vanity_name(self, vanity_name: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/rest/organizations",
            params={"q": "vanityName", "vanityName": vanity_name},
        )

    async def list_organization_posts(
        self,
        organization_id: str,
        *,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        org_urn = _organization_urn(organization_id)
        return await self.list_posts(org_urn, count=count, start=start)

    async def get_job(self, job_id: str) -> dict[str, Any]:
        encoded = quote(job_id, safe="")
        return await self._request("GET", f"/rest/jobs/{encoded}")

    async def search_jobs(
        self,
        *,
        keywords: str,
        location: str | None = None,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"keywords": keywords, "count": count, "start": start}
        if location:
            params["location"] = location
        return await self._request("GET", "/rest/jobs", params=params)

    # ------------------------------------------------------------------
    # Events  (r_events / rw_events)
    # ------------------------------------------------------------------

    async def list_organization_events(
        self,
        organization_id: str,
        *,
        count: int = 10,
        start: int = 0,
    ) -> dict[str, Any]:
        org_urn = _organization_urn(organization_id)
        return await self._request(
            "GET",
            "/rest/events",
            params={
                "q": "eventsByOrganizer",
                "organizer": org_urn,
                "count": count,
                "start": start,
                "excludeCancelled": True,
            },
        )

    async def get_event(self, event_id: str) -> dict[str, Any]:
        encoded = quote(event_id, safe="")
        return await self._request("GET", f"/rest/events/{encoded}")

    async def create_event(self, event: EventInput) -> dict[str, Any]:
        org_urn = _organization_urn(event.organization_id)
        payload: dict[str, Any] = {
            "organizer": org_urn,
            "name": event.name,
            "eventStartAt": event.start_at,
            "eventEndAt": event.end_at,
            "entryCriteria": "PUBLIC",
        }
        if event.description:
            payload["description"] = event.description

        if event.event_type.value == "EXTERNAL":
            payload["type"] = {
                "external": {
                    "externalUrl": str(event.event_url) if event.event_url else "",
                },
            }
        else:
            payload["type"] = {"inPerson": {}}

        return await self._request("POST", "/rest/events", json=payload)

    # ------------------------------------------------------------------
    # Media / Image upload  (w_member_social)
    # ------------------------------------------------------------------

    async def register_image_upload(self, owner_urn: str | None = None) -> dict[str, Any]:
        if not owner_urn:
            owner_urn = await self._author_urn()
        return await self._request(
            "POST",
            "/v2/assets?action=registerUpload",
            json={
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": owner_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent",
                        }
                    ],
                }
            },
            restli=False,
        )

    async def upload_image(self, upload_url: str, image_data: bytes) -> int:
        from urllib.parse import urlparse
        parsed = urlparse(upload_url)
        if parsed.hostname not in ("api.linkedin.com", "www.linkedin.com"):
            raise LinkedInConfigError("upload_url must point to a LinkedIn API domain")
        headers = {"Authorization": f"Bearer {self.config.access_token}"}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(upload_url, content=image_data, headers=headers)
        if resp.is_error:
            raise LinkedInAPIError(resp.status_code, "Image upload failed", None)
        return resp.status_code

    async def create_image_post(self, post: ImagePostInput) -> dict[str, Any]:
        author = await self._author_urn()
        payload: dict[str, Any] = {
            "author": author,
            "commentary": post.text,
            "visibility": post.visibility.value,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "media": {
                    "id": post.image_urn,
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        media = payload["content"]["media"]
        if post.image_title:
            media["title"] = post.image_title
        if post.image_alt_text:
            media["altText"] = post.image_alt_text
        return await self._request("POST", "/rest/posts", json=payload)

    async def api_get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        restli: bool = True,
    ) -> dict[str, Any]:
        return await self._request("GET", _safe_api_path(path), params=params, restli=restli)

    async def api_post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        restli: bool = True,
    ) -> dict[str, Any]:
        return await self._request(
            "POST", _safe_api_path(path), json=json, params=params, restli=restli
        )

    async def _author_urn(self) -> str:
        if self.config.member_urn:
            return _normalize_author_urn(self.config.member_urn)

        try:
            profile = await self.get_me()
        except LinkedInAPIError as exc:
            if exc.status_code == 403:
                raise LinkedInConfigError(
                    "Cannot determine LinkedIn author URN with the current token. "
                    "LinkedIn denied self-profile lookup for this app/token. "
                    "Set LINKEDIN_MEMBER_URN or call linkedin_set_member_urn with your "
                    "urn:li:person:... value, then retry posting."
                ) from exc
            raise
        subject = profile.get("sub") or profile.get("id")
        if not subject:
            raise LinkedInAPIError(
                200,
                "LinkedIn profile response did not include 'sub' or 'id'",
                profile,
            )
        return f"urn:li:person:{subject}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        restli: bool = True,
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.config.access_token}",
            "Accept": "application/json",
        }
        if restli:
            headers.update(
                {
                    "LinkedIn-Version": self.config.api_version,
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                }
            )

        async with httpx.AsyncClient(base_url=API_BASE, timeout=30) as client:
            response = await client.request(method, path, headers=headers, json=json, params=params)

        if response.is_error:
            raise LinkedInAPIError(
                response.status_code,
                _error_message(response),
                _safe_json(response),
            )
        if response.status_code == 201 and response.headers.get("x-restli-id"):
            return {"id": response.headers["x-restli-id"], "status_code": response.status_code}
        if not response.content:
            return {"status_code": response.status_code}
        return response.json()


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text


def _error_message(response: httpx.Response) -> str:
    details = _safe_json(response)
    if isinstance(details, dict):
        message = details.get("message") or details.get("error_description") or details.get("error")
        if message:
            return str(message)
    return f"LinkedIn API request failed with status {response.status_code}"


def _normalize_author_urn(value: str) -> str:
    if value.startswith("urn:li:member:"):
        return "urn:li:person:" + value.removeprefix("urn:li:member:")
    return value


def _organization_id(value: str) -> str:
    value = value.strip()
    if value.startswith("urn:li:organization:"):
        return value.removeprefix("urn:li:organization:")
    return value


def _organization_urn(value: str) -> str:
    value = _organization_id(value)
    return f"urn:li:organization:{value}"


def _safe_api_path(path: str) -> str:
    path = path.strip()
    if not path.startswith("/"):
        path = f"/{path}"
    if not (path.startswith("/rest/") or path.startswith("/v2/")):
        raise LinkedInConfigError("path must start with /rest/ or /v2/")
    if ".." in path or "//" in path:
        raise LinkedInConfigError("path must not contain '..' or '//'")
    return path
