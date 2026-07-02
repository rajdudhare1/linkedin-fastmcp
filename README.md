# LinkedIn FastMCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

> MCP server for LinkedIn REST APIs. Give any MCP-compatible AI coding agent the ability to create posts, upload images, manage comments, reactions, events, and more -- all via official LinkedIn APIs.

**This project is independent and not affiliated with, authorized by, endorsed by, or sponsored by LinkedIn Corporation or Microsoft.**

---

## Features

- **OAuth 2.0** -- Full 3-legged OAuth flow with native MCP OAuth support (OpenCode auto-auth)
- **Posts** -- Create, list, get, delete text and link posts
- **Image Posts** -- Register, upload, and publish image posts (3-step workflow)
- **Comments** -- Create, reply, get, delete comments on any activity
- **Reactions** -- Like, unlike, repost, get social action metadata
- **Organizations** -- List admin orgs, get org details, post as org, list org posts
- **Events** -- List, get, create organization events (in-person + external)
- **Profile** -- Get authenticated member profile, email, basic info, verification status
- **Escape Hatch** -- `api_get` and `api_post` for any `/rest` or `/v2` LinkedIn endpoint
- **Security Hardened** -- SSRF protection, XSS prevention, token masking, input validation

---

## Quick Start

### 1. Create a LinkedIn App

Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) and create an app. Add these products:

| Product | Scopes Granted |
|---|---|
| **Sign In with LinkedIn using OpenID Connect** | `openid`, `profile`, `email` |
| **Share on LinkedIn** | `w_member_social` |
| **Events Management API** | `r_events`, `rw_events` |

Set the redirect URI to `http://localhost:8000/callback`.

### 2. Install

```bash
pip install -e .
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET
```

### 4. Run

```bash
# stdio mode (for local MCP clients)
python3 -m linkedin_fastmcp

# HTTP mode (for remote MCP clients / Docker)
python3 -m linkedin_fastmcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

### 5. Authenticate

```bash
# Option A: OpenCode handles it automatically (recommended)
opencode mcp auth linkedin-fastmcp

# Option B: Manual flow
# 1. Call linkedin_get_auth_url tool
# 2. Open the URL, approve, copy the code
# 3. Call linkedin_exchange_code_for_token with the code
```

---

## Docker

```bash
# Build
docker build -t linkedin-fastmcp:latest .

# Run
docker run --rm -p 8000:8000 \
  -e LINKEDIN_CLIENT_ID=your-client-id \
  -e LINKEDIN_CLIENT_SECRET=your-client-secret \
  linkedin-fastmcp:latest
```

---

## MCP Client Configuration

### OpenCode (Recommended)

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "linkedin-fastmcp": {
      "type": "remote",
      "url": "http://localhost:8000/mcp",
      "enabled": true,
      "oauth": {
        "clientId": "{env:LINKEDIN_CLIENT_ID}",
        "clientSecret": "{env:LINKEDIN_CLIENT_SECRET}",
        "scope": "openid profile email r_profile_basicinfo w_member_social r_events rw_events"
      }
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "linkedin-fastmcp": {
      "command": "python3",
      "args": ["-m", "linkedin_fastmcp"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your-client-id",
        "LINKEDIN_CLIENT_SECRET": "your-client-secret",
        "LINKEDIN_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

### Claude Desktop (Docker)

```json
{
  "mcpServers": {
    "linkedin-fastmcp": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "LINKEDIN_CLIENT_ID=your-client-id",
        "-e", "LINKEDIN_CLIENT_SECRET=your-client-secret",
        "-e", "LINKEDIN_ACCESS_TOKEN=your-access-token",
        "linkedin-fastmcp:latest",
        "--transport", "stdio"
      ]
    }
  }
}
```

### Cursor / Windsurf / VS Code (Copilot)

```json
{
  "mcpServers": {
    "linkedin-fastmcp": {
      "command": "python3",
      "args": ["-m", "linkedin_fastmcp"],
      "env": {
        "LINKEDIN_CLIENT_ID": "your-client-id",
        "LINKEDIN_CLIENT_SECRET": "your-client-secret",
        "LINKEDIN_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

For Cursor, add this to `.cursor/mcp.json` in your project.
For Windsurf, add this to `~/.codeium/windsurf/mcp_config.json`.

---

## Tool Catalog (36 Tools)

### Auth & Profile (9 tools)

| Tool | Description |
|---|---|
| `linkedin_get_auth_url` | Generate OAuth authorization URL |
| `linkedin_exchange_code_for_token` | Exchange auth code for access token |
| `linkedin_validate_credentials` | Validate current token/config |
| `linkedin_get_supported_actions` | List available actions for current scopes |
| `linkedin_set_member_urn` | Set member URN manually |
| `linkedin_get_me` | Get profile via OpenID Connect |
| `linkedin_get_basic_profile` | Get profile via `/v2/me` |
| `linkedin_get_email` | Get primary email address |
| `linkedin_get_verification_status` | Check verification status (`r_verify`) |

### Posts (6 tools)

| Tool | Scope | Description |
|---|---|---|
| `linkedin_create_text_post` | `w_member_social` | Create text post |
| `linkedin_create_link_post` | `w_member_social` | Create link/article post |
| `linkedin_list_posts` | `w_member_social` | List your posts |
| `linkedin_get_post` | `w_member_social` | Get post by URN |
| `linkedin_delete_post` | `w_member_social` | Delete post |
| `linkedin_repost` | `w_member_social` | Repost with optional commentary |

### Media / Image Posts (3 tools)

| Tool | Description |
|---|---|
| `linkedin_register_image_upload` | Register upload, get upload URL + asset URN |
| `linkedin_upload_image` | Upload base64 image to the upload URL |
| `linkedin_create_image_post` | Create post with uploaded image |

**Workflow:** `register` -> `upload` -> `create_image_post`

### Comments & Engagement (8 tools)

| Tool | Description |
|---|---|
| `linkedin_create_comment` | Comment on a post |
| `linkedin_get_comments` | Get comments |
| `linkedin_reply_to_comment` | Reply to a comment |
| `linkedin_delete_comment` | Delete a comment |
| `linkedin_get_social_action` | Get social metadata |
| `linkedin_list_likes` | List likes |
| `linkedin_like_activity` | Like a post |
| `linkedin_unlike_activity` | Unlike a post |

### Organizations (6 tools)

| Tool | Description |
|---|---|
| `linkedin_list_admin_organizations` | List orgs you admin |
| `linkedin_get_organization` | Get org by ID |
| `linkedin_get_organization_by_vanity_name` | Get org by vanity name |
| `linkedin_create_organization_text_post` | Post text as org |
| `linkedin_create_organization_link_post` | Post link as org |
| `linkedin_list_organization_posts` | List org posts |

### Events (3 tools)

| Tool | Scope | Description |
|---|---|---|
| `linkedin_list_organization_events` | `r_events` | List org events |
| `linkedin_get_event` | `r_events` | Get event by ID |
| `linkedin_create_event` | `rw_events` | Create org event |

### Advanced / Escape Hatch (4 tools)

| Tool | Description |
|---|---|
| `linkedin_api_get` | GET any `/rest` or `/v2` endpoint |
| `linkedin_api_post` | POST any `/rest` or `/v2` endpoint |
| `linkedin_get_job` | Get job by ID |
| `linkedin_search_jobs` | Search jobs |

---

## API Boundaries

LinkedIn does **not** expose public APIs for:

| Operation | Reason |
|---|---|
| Edit profile (headline, about, skills) | No public API exists |
| Read other people's profiles | Requires partner access |
| Search people/companies | Requires partner access |
| Send messages/InMail | Requires SNAP partner |
| Read connections list | Deprecated/restricted |
| Post analytics | Requires Marketing API partner |

These are only available through LinkedIn's own web/mobile interfaces or restricted partner programs.

---

## Architecture

```
src/linkedin_fastmcp/
├── cli.py              # CLI entrypoint
├── config.py           # Configuration (env vars + token store)
├── errors.py           # Error hierarchy
├── linkedin_client.py  # LinkedIn REST API client (all HTTP calls)
├── mcp_oauth.py        # MCP-level OAuth state machine
├── oauth.py            # LinkedIn OAuth helpers
├── oauth_callback.py   # Standalone OAuth callback server
├── schemas.py          # Pydantic input models
├── server.py           # FastMCP server + OAuth routes
├── token_store.py      # Token persistence
└── tools/
    ├── __init__.py     # Tool registration
    ├── api.py          # Escape hatch + jobs
    ├── auth.py         # OAuth tools
    ├── comments.py     # Comment CRUD
    ├── events.py       # Event tools
    ├── media.py        # Image upload + posts
    ├── organizations.py # Org tools
    ├── posts.py        # Post CRUD
    ├── profile.py      # Profile + email + verification
    └── reactions.py    # Like/unlike/repost
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `LINKEDIN_CLIENT_ID` | Yes | OAuth app client ID |
| `LINKEDIN_CLIENT_SECRET` | Yes | OAuth app client secret |
| `LINKEDIN_REDIRECT_URI` | No | Callback URL (default: `http://localhost:8000/callback`) |
| `LINKEDIN_ACCESS_TOKEN` | No | Pre-set access token (skips OAuth flow) |
| `LINKEDIN_MEMBER_URN` | No | Override member URN (e.g. `urn:li:person:abc123`) |
| `LINKEDIN_SCOPES` | No | Space-separated scopes (has sensible defaults) |
| `LINKEDIN_API_VERSION` | No | LinkedIn API version (default: `202602`) |
| `LINKEDIN_TOKEN_FILE` | No | Custom token file path |

---

## Development

```bash
pip install -e '.[dev]'
python3 -m pytest -v       # Run tests
python3 -m ruff check .    # Lint
```

---

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security practices.

---

## License

[MIT License](LICENSE) -- Free for personal and commercial use.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
