"""
Web Search MCP Server

Exposes web search as an MCP tool over stdio transport.
In production, swap the mock implementation for Brave Search / SerpAPI.
Run standalone: python -m app_ADK.mcp_servers.search_server
"""

import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Logger ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | MCP:search | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mcp.search")

# ── MCP Server ────────────────────────────────────────────────────────────────
server = Server("search-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_web",
            description="Search the web and return relevant results for a query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("Tool called: %s | args: %s", name, arguments)

    if name != "search_web":
        result = {"error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result))]

    query = arguments.get("query", "").strip()
    if not query:
        result = {"error": "Empty query provided."}
        return [TextContent(type="text", text=json.dumps(result))]

    # ── Mock results (swap for real API call here) ─────────────────────────
    results = [
        {
            "title":   f"Everything about '{query}'",
            "snippet": f"Comprehensive overview of {query} — history, key concepts, latest developments.",
            "url":     f"https://example.com/search?q={query.replace(' ', '+')}",
        },
        {
            "title":   f"{query} — Wikipedia",
            "snippet": f"Wikipedia article on {query} with background and references.",
            "url":     f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
        },
        {
            "title":   f"Latest news on {query}",
            "snippet": f"Breaking news and recent updates related to {query}.",
            "url":     f"https://news.example.com/?q={query.replace(' ', '+')}",
        },
    ]

    result = {"query": query, "count": len(results), "results": results}
    logger.info("Search for '%s' returned %d results", query, len(results))

    return [TextContent(type="text", text=json.dumps(result))]


async def main():
    logger.info("Search MCP server starting (stdio transport)")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
