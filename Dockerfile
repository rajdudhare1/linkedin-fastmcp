FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

ENTRYPOINT ["linkedin-fastmcp"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000", "--path", "/mcp"]
