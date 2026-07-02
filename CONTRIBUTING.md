# Contributing

Contributions are welcome! Please follow these guidelines.

## Getting Started

```bash
git clone https://github.com/rajdudhare1/linkedin-fastmcp.git
cd linkedin-fastmcp/mcp-servers/linkedin-fastmcp
pip install -e '.[dev]'
```

## Development Workflow

1. **Create a branch** from `main`
2. **Make changes** in `src/linkedin_fastmcp/`
3. **Add tests** in `tests/`
4. **Run checks:**
   ```bash
   python3 -m pytest -v
   python3 -m ruff check .
   ```
5. **Submit a pull request**

## Code Style

- Python 3.11+ type hints required
- Max line length: 100 characters
- Linter: `ruff` (rules: E, F, I, UP, B)
- All tools must follow the existing pattern:
  - Return `{"ok": True, ...}` on success
  - Return `error.as_dict()` for API errors
  - Return `{"ok": False, "error": ..., "message": ...}` for other errors
  - Use Pydantic models for input validation
  - Tag tools with relevant categories

## Adding a New Tool

1. Add the client method to `linkedin_client.py`
2. Add the Pydantic schema to `schemas.py` (if needed)
3. Create or extend a tool file in `tools/`
4. Register the tool in `tools/__init__.py`
5. Add tests
6. Update `README.md` tool catalog

## Security

- Never return full access tokens to MCP clients
- Validate all URLs before sending credentials
- Escape all HTML output
- Use Pydantic for input validation
- Read the `SECURITY.md` before working on auth-related code

## Testing

```bash
# All tests
python3 -m pytest -v

# Single file
python3 -m pytest tests/test_events.py -v

# With coverage
python3 -m pytest --cov=linkedin_fastmcp
```

## Issues

Please open an issue before submitting a PR for non-trivial changes.
