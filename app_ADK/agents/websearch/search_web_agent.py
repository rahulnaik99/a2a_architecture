"""
Web Search Agent — backed by the Search MCP Server (stdio transport).

Connects to mcp_servers/search_server.py at runtime.
Swap the mock server for Brave Search / SerpAPI in production.
"""

import sys
import logging
from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

logger = logging.getLogger(__name__)

SKILLS          = (Path(__file__).parent / "skills.md").read_text()
_SERVER_SCRIPT  = str(Path(__file__).parent.parent.parent / "mcp_servers" / "search_server.py")


def create_agent() -> Agent:
    logger.info("Creating search_agent with MCP server: %s", _SERVER_SCRIPT)

    return Agent(
        name="search_agent",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        description=(
            "Searches the web for any query and returns relevant results "
            "using the search_web MCP tool."
        ),
        instruction=f"""
You are a web search assistant backed by a live MCP search tool.

Use the search_web tool to find information for the user's query.
Summarize the top results clearly and always include source URLs.

{SKILLS}
""",
        tools=[
            MCPToolset(
                connection_params=StdioServerParameters(
                    command=sys.executable,
                    args=[_SERVER_SCRIPT],
                )
            )
        ],
    )
