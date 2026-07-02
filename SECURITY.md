# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, email: **rajdudhare1@gmail.com** with:

1. Description of the vulnerability
2. Steps to reproduce
3. Impact assessment
4. Suggested fix (if any)

You will receive acknowledgment within 48 hours and a detailed response within 7 days.

## Security Measures

This project implements the following security practices:

### Token Handling
- Access tokens are **never** returned in full to the LLM/MCP client
- Tokens are stored locally in `~/.config/linkedin-fastmcp/token.json` with user-only permissions
- Token previews (first 8 chars) are shown instead of full values
- No tokens are logged or printed in full to stdout

### Input Validation
- All user inputs are validated via Pydantic models
- API paths are restricted to `/rest/` and `/v2/` prefixes with `..` and `//` blocked
- Image upload URLs are validated against LinkedIn API domains only (SSRF protection)
- OAuth redirect URIs are restricted to localhost only (open redirect protection)

### Web Security
- All HTML output is escaped to prevent XSS
- OAuth state parameters use cryptographically random tokens
- Authorization codes and state tokens are single-use
- In-memory OAuth state is bounded (max 1000 entries) to prevent DoS

### API Security
- All LinkedIn API calls use Bearer token authentication over HTTPS
- No credentials are hardcoded or baked into Docker images
- Environment variables are the only source for secrets

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Dependencies

This project depends on:
- `fastmcp` - MCP protocol implementation
- `httpx` - HTTP client (HTTPS enforced for LinkedIn API)
- `pydantic` - Input validation
- `python-dotenv` - Environment variable loading

All dependencies are pinned to minimum versions in `pyproject.toml`.
