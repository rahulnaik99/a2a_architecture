"""
Weather Agent — backed by the Weather MCP Server (stdio transport).

The agent connects to mcp_servers/weather_server.py at runtime.
No function tools — all tool calls go through MCP.
"""

import sys
import logging
from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

logger = logging.getLogger(__name__)

SKILLS          = (Path(__file__).parent / "skills.md").read_text()
_SERVER_SCRIPT  = str(Path(__file__).parent.parent.parent / "mcp_servers" / "weather_server.py")


def create_agent() -> Agent:
    logger.info("Creating weather_agent with MCP server: %s", _SERVER_SCRIPT)

    return Agent(
        name="weather_agent",
        model=LiteLlm(model="openai/gpt-4o-mini"),
        description=(
            "Retrieves current weather (temperature, humidity, conditions) for a city "
            "using the get_weather MCP tool."
        ),
        instruction=f"""
You are a helpful weather assistant backed by a live MCP weather tool.

Use the get_weather tool to fetch weather data for the requested city.
Always report:
- Temperature in Celsius AND Fahrenheit
- Humidity percentage
- Weather condition

Respond ONLY with the raw JSON from the tool — no extra commentary.

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
