"""
Calculator Agent — backed by the Calculator MCP Server (stdio transport).

Connects to mcp_servers/calculator_server.py at runtime.
"""

import sys
import logging
from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

logger = logging.getLogger(__name__)

SKILLS          = (Path(__file__).parent / "skiils.md").read_text()
_SERVER_SCRIPT  = str(Path(__file__).parent.parent.parent / "mcp_servers" / "calculator_server.py")


def create_agent() -> Agent:
    logger.info("Creating calculator_agent with MCP server: %s", _SERVER_SCRIPT)

    return Agent(
        name="calculator_agent",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        description=(
            "Evaluates mathematical expressions using the calculate MCP tool. "
            "Handles arithmetic, averages, percentages, and math functions."
        ),
        instruction=f"""
You are a precise calculator assistant backed by a live MCP calculator tool.

Use the calculate tool to evaluate the mathematical expression given to you.
- Pass the expression exactly as received (with resolved numeric values).
- Respond ONLY with the raw JSON from the tool — no extra commentary.

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
