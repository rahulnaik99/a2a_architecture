"""
Weather MCP Server

Exposes weather lookup as a real MCP tool over stdio transport.
Run standalone: python -m app_ADK.mcp_servers.weather_server

Agents connect to this via StdioServerParameters — no HTTP, no port needed.
"""

import json
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as mcp_types

# ── Logger ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | MCP:weather | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mcp.weather")

# ── Mock data ─────────────────────────────────────────────────────────────────
WEATHER_DATA = {
    "london":   {"temp_c": 14, "condition": "Cloudy",        "humidity": 78},
    "new york": {"temp_c": 22, "condition": "Sunny",         "humidity": 55},
    "tokyo":    {"temp_c": 28, "condition": "Humid",         "humidity": 85},
    "paris":    {"temp_c": 18, "condition": "Partly Cloudy", "humidity": 65},
    "sydney":   {"temp_c": 20, "condition": "Clear",         "humidity": 60},
    "delhi":    {"temp_c": 35, "condition": "Hot",           "humidity": 40},
    "mumbai":   {"temp_c": 30, "condition": "Humid",         "humidity": 70},
}

SUPPORTED_CITIES = [c.title() for c in WEATHER_DATA]

# ── MCP Server ────────────────────────────────────────────────────────────────
server = Server("weather-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description=(
                "Get current weather for a city. "
                f"Supported cities: {', '.join(SUPPORTED_CITIES)}."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": f"City name. One of: {', '.join(SUPPORTED_CITIES)}",
                    }
                },
                "required": ["city"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("Tool called: %s | args: %s", name, arguments)

    if name != "get_weather":
        logger.warning("Unknown tool requested: %s", name)
        result = {"error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result))]

    city = arguments.get("city", "").strip()
    key  = city.lower()

    if key not in WEATHER_DATA:
        result = {
            "error": f"No weather data for '{city}'.",
            "supported_cities": SUPPORTED_CITIES,
        }
        logger.warning("City not found: %s", city)
    else:
        data   = WEATHER_DATA[key]
        result = {
            "city":      city.title(),
            "temp_c":    data["temp_c"],
            "temp_f":    round(data["temp_c"] * 9 / 5 + 32, 1),
            "condition": data["condition"],
            "humidity":  data["humidity"],
        }
        logger.info("Weather result: %s", result)

    return [TextContent(type="text", text=json.dumps(result))]


async def main():
    logger.info("Weather MCP server starting (stdio transport)")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
