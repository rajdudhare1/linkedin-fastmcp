<div align="center">

# LinkedIn FastMCP

### Give your AI coding agent superpowers on LinkedIn

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-brightgreen.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-43%20passed-success.svg)]()
[![Security](https://img.shields.io/badge/security-hardened-blueviolet.svg)](SECURITY.md)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker&logoColor=white)]()
[![LinkedIn API](https://img.shields.io/badge/LinkedIn-API%20v2-0A66C2.svg?logo=linkedin&logoColor=white)](https://learn.microsoft.com/en-us/linkedin/)

<br/>

**36 tools** &bull; **API-only** (no browser scraping) &bull; **OAuth 2.0** &bull; **Security hardened**

[Getting Started](#quick-start) &bull; [Tool Catalog](#tool-catalog-36-tools) &bull; [IDE Setup](#mcp-client-configuration) &bull; [Docker](#docker) &bull; [Contributing](CONTRIBUTING.md)

</div>

---

> An open-source MCP server that connects AI coding agents to LinkedIn's official REST APIs. Create posts, upload images, manage comments, reactions, organization pages, events -- all through the Model Context Protocol.

**This project is independent and not affiliated with, authorized by, endorsed by, or sponsored by LinkedIn Corporation or Microsoft.**

---

## Why LinkedIn FastMCP?

| | Browser Scraping MCP Servers | **LinkedIn FastMCP** |
|---|---|---|
| **Method** | Headless browser automation | Official LinkedIn REST APIs |
| **Write Operations** | Fragile, often broken | Reliable, API-backed |
| **Auth** | Cookie-based sessions | OAuth 2.0 with token refresh |
| **Account Risk** | Possible restrictions | Zero risk (official APIs) |
| **Image Posts** | Not supported | Full 3-step upload workflow |
| **Events** | Not supported | Create, list, get org events |
| **Speed** | Slow (page loads) | Fast (direct API calls) |
| **Docker** | Complex (Chromium deps) | Lightweight Python image |

---

## Features

- **Posts** -- Create, list, get, delete text and link posts
- **Image Posts** -- Register, upload, and publish image posts (3-step workflow)
- **Comments** -- Create, reply, get, delete comments on any activity
- **Reactions** -- Like, unlike, repost, get social action metadata
- **Organizations** -- List admin orgs, get org details, post as org, list org posts
- **Events** -- List, get, create organization events (in-person + external)
- **Profile** -- Get authenticated member profile, email, basic info, verification status
- **OAuth 2.0** -- Full 3-legged flow with native MCP OAuth support
- **Escape Hatch** -- `api_get` and `api_post` for any `/rest` or `/v2` LinkedIn endpoint
- **Security** -- SSRF protection, XSS prevention, token masking, input validation

---

## Quick Start

### 1. Create a LinkedIn App

Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) and create an app. Add these products:

| Product | Scopes Granted |
|---|---|
| **Sign In with LinkedIn using OpenID Connect** | `openid`, `profile`, `email` |
| **Share on LinkedIn** | `w_member_social` |
| **Events Management API** *(optional)* | `r_events`, `rw_events` |

Set the redirect URI to `http://localhost:8000/callback`.

### 2. Install & Run

```bash
git clone https://github.com/rajdudhare1/linkedin-fastmcp.git
cd linkedin-fastmcp/mcp-servers/linkedin-fastmcp
pip install -e .
```

```bash
cp .env.example .env
# Add your LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to .env
```

```bash
# stdio mode (local MCP clients)
python3 -m linkedin_fastmcp

# HTTP mode (remote MCP clients / Docker)
python3 -m linkedin_fastmcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

### 3. Authenticate

OpenCode handles auth automatically. Or manually:

```bash
opencode mcp auth linkedin-fastmcp
```

---

## Docker

```bash
docker build -t linkedin-fastmcp:latest .

docker run --rm -p 8000:8000 \
  -e LINKEDIN_CLIENT_ID=your-client-id \
  -e LINKEDIN_CLIENT_SECRET=your-client-secret \
  linkedin-fastmcp:latest
```

No secrets baked into the image. Pass credentials at runtime via `-e` or `--env-file .env`.

---

## MCP Client Configuration

<details>
<summary><b>OpenCode</b> (Recommended -- native OAuth support)</summary>

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "mcp": {
    "linkedin-fastmcp": {
      "type": "remote",
      "url": "http://localhost:8000/mcp",
      "oauth": {
        "clientId": "{env:LINKEDIN_CLIENT_ID}",
        "clientSecret": "{env:LINKEDIN_CLIENT_SECRET}",
        "scope": "openid profile email r_profile_basicinfo w_member_social r_events rw_events"
      }
    }
  }
}
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

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
</details>

<details>
<summary><b>Claude Desktop (Docker)</b></summary>

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
</details>

<details>
<summary><b>Cursor</b></summary>

Add to `.cursor/mcp.json`:

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
</details>

<details>
<summary><b>Windsurf</b></summary>

Add to `~/.codeium/windsurf/mcp_config.json`:

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
</details>

<details>
<summary><b>VS Code (GitHub Copilot)</b></summary>

Add to `.vscode/mcp.json`:

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
</details>

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
| `linkedin_get_verification_status` | Check verification status |

### Posts (6 tools)

| Tool | Description |
|---|---|
| `linkedin_create_text_post` | Create text post |
| `linkedin_create_link_post` | Create link/article post |
| `linkedin_list_posts` | List your posts |
| `linkedin_get_post` | Get post by URN |
| `linkedin_delete_post` | Delete post |
| `linkedin_repost` | Repost with optional commentary |

### Media / Image Posts (3 tools)

| Tool | Description |
|---|---|
| `linkedin_register_image_upload` | Register upload, get URL + asset URN |
| `linkedin_upload_image` | Upload base64 image to the upload URL |
| `linkedin_create_image_post` | Create post with uploaded image |

> **Workflow:** `register` &rarr; `upload` &rarr; `create_image_post`

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

| Tool | Description |
|---|---|
| `linkedin_list_organization_events` | List org events |
| `linkedin_get_event` | Get event by ID |
| `linkedin_create_event` | Create org event |

### Advanced / Escape Hatch (4 tools)

| Tool | Description |
|---|---|
| `linkedin_api_get` | GET any `/rest` or `/v2` endpoint |
| `linkedin_api_post` | POST any `/rest` or `/v2` endpoint |
| `linkedin_get_job` | Get job by ID |
| `linkedin_search_jobs` | Search jobs |

---

## Architecture

```
src/linkedin_fastmcp/
├── cli.py              # CLI entrypoint
├── config.py           # Configuration (env vars + token store)
├── errors.py           # Error hierarchy
├── linkedin_client.py  # LinkedIn REST API client
├── mcp_oauth.py        # MCP-level OAuth state machine
├── oauth.py            # LinkedIn OAuth helpers
├── oauth_callback.py   # Standalone OAuth callback server
├── schemas.py          # Pydantic input models
├── server.py           # FastMCP server + OAuth routes
├── token_store.py      # Token persistence
└── tools/              # 9 tool modules (36 tools)
```

---

## API Boundaries

LinkedIn does **not** expose public APIs for:

| Operation | Reason |
|---|---|
| Edit profile (headline, about, skills) | No public API |
| Read other people's profiles | Partner access required |
| Search people/companies | Partner access required |
| Send messages/InMail | SNAP partner required |
| Post analytics | Marketing API partner required |

---

## Environment Variables

| Variable | Required | Default |
|---|---|---|
| `LINKEDIN_CLIENT_ID` | Yes | -- |
| `LINKEDIN_CLIENT_SECRET` | Yes | -- |
| `LINKEDIN_REDIRECT_URI` | No | `http://localhost:8000/callback` |
| `LINKEDIN_ACCESS_TOKEN` | No | Token store |
| `LINKEDIN_MEMBER_URN` | No | Auto-derived |
| `LINKEDIN_SCOPES` | No | All available scopes |
| `LINKEDIN_API_VERSION` | No | `202602` |

---

## Security

This project is security hardened. See [SECURITY.md](SECURITY.md) for details.

- SSRF protection on image uploads (LinkedIn domains only)
- XSS prevention in OAuth callback HTML
- Access tokens never returned in full to LLM clients
- OAuth redirect URIs restricted to localhost
- Bounded in-memory state (DoS prevention)
- All inputs validated via Pydantic

---

## Development

```bash
pip install -e '.[dev]'
python3 -m pytest -v       # 43 tests
python3 -m ruff check .    # Lint
```

---

## License

[MIT License](LICENSE) -- Free for personal and commercial use.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

<div align="center">

**Built with [FastMCP](https://gofastmcp.com/) &bull; Powered by [LinkedIn REST APIs](https://learn.microsoft.com/en-us/linkedin/)**

Made with &#10084; by [Raj Dudhare](https://github.com/rajdudhare1)

</div>
