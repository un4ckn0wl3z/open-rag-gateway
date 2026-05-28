import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from .backend_client import BackendClient
from .config import get_settings

settings = get_settings()
client = BackendClient()
mcp = FastMCP("project-rag-mcp", host=settings.host, port=settings.port)


def _format_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


@mcp.tool()
def retrieve_context(query: str, top_k: int = 8) -> str:
    """Retrieve top-k relevant chunks from the indexed project context."""
    result = client.retrieve_context(query=query, top_k=top_k)
    return _format_json(result)


@mcp.tool()
def list_sections() -> str:
    """List available section headings from the indexed project context."""
    result = client.list_sections()
    return _format_json(result)


@mcp.tool()
def cite_sources(chunk_ids: list[str]) -> str:
    """Return citations for provided chunk IDs."""
    result = client.cite_sources(chunk_ids=chunk_ids)
    return _format_json(result)


@mcp.tool()
def retrieve_internal_skill(query: str, top_k: int = 8) -> str:
    """Deprecated alias for retrieve_context(query, top_k)."""
    return retrieve_context(query=query, top_k=top_k)


@mcp.tool()
def list_skill_sections() -> str:
    """Deprecated alias for list_sections()."""
    return list_sections()


if __name__ == "__main__":
    transport = settings.transport.lower().strip()
    if transport not in {"stdio", "sse"}:
        raise RuntimeError("MCP_TRANSPORT must be 'stdio' or 'sse'")

    if transport == "sse":
        # Prefer explicit host/port, but keep compatibility with SDKs that
        # only accept the transport argument.
        try:
            mcp.run(transport="sse", host=settings.host, port=settings.port)
        except TypeError:
            mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
