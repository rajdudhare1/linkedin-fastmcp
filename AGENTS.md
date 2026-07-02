# AGENTS.md

## Project Shape
- Python package using the `src/` layout; install locally with `pip install -e '.[dev]'` to get runtime deps plus `pytest` and `ruff`.
- CLI entrypoint is `linkedin-fastmcp = linkedin_fastmcp.cli:main`; `python3 -m linkedin_fastmcp` calls the same CLI.
- `src/linkedin_fastmcp/server.py` creates the FastMCP server and registers tool groups from `src/linkedin_fastmcp/tools/`.
- **API-only project** -- no browser automation. All tools use LinkedIn REST APIs via `LinkedInClient`.

## Verification Commands
- Run all tests: `python3 -m pytest`.
- Run one test file or focused test: `python3 -m pytest tests/test_config.py` or `python3 -m pytest tests/test_config.py -k load_config`.
- Run lint: `python3 -m ruff check .`.

## LinkedIn/OAuth Gotchas
- Do not read or modify `.env`; it is ignored and may contain real LinkedIn credentials. Use `.env.example` for variable names and defaults.
- `load_config()` loads `.env` by default and then falls back to the token store when `LINKEDIN_ACCESS_TOKEN` / `LINKEDIN_MEMBER_URN` are unset.
- Token store default is `~/.config/linkedin-fastmcp/token.json`; tests override it with `LINKEDIN_TOKEN_FILE`.
- OAuth callback is built into `streamable-http` mode at `/callback` on the same host/port as the MCP server, while the standalone helper uses `--oauth-callback-server --callback-port 8080`.
- Posting, commenting, and event creation tools are marked destructive; profile/auth validation tools are read-only helpers.

## API Details To Preserve
- LinkedIn REST API calls require `LinkedIn-Version` from `LINKEDIN_API_VERSION` and `X-Restli-Protocol-Version: 2.0.0`; this is centralized in `LinkedInClient._request`.
- Author URN comes from `LINKEDIN_MEMBER_URN`, token-store `member_urn`, `/v2/userinfo` `sub`, or `/v2/me` `id`; keep that fallback order unless changing tests.
- Default scopes include `openid profile email r_profile_basicinfo w_member_social r_events rw_events`; `LINKEDIN_SCOPES` accepts comma or space separated values.

## Tool Groups
- `tools/auth.py` -- OAuth flow, credential validation, supported actions
- `tools/profile.py` -- Profile read, basic profile, email, verification status
- `tools/posts.py` -- Personal text/link post CRUD
- `tools/media.py` -- Image upload workflow (register, upload, create image post)
- `tools/comments.py` -- Comment CRUD on activities
- `tools/reactions.py` -- Like/unlike, repost, social action metadata
- `tools/organizations.py` -- Org lookup, org-authored posts
- `tools/events.py` -- Organization event list/get/create (r_events/rw_events)
- `tools/api.py` -- Escape-hatch GET/POST for any /rest or /v2 endpoint, plus jobs
