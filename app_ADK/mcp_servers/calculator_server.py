"""
Calculator MCP Server

Exposes safe math evaluation as an MCP tool over stdio transport.
Run standalone: python -m app_ADK.mcp_servers.calculator_server
"""

import json
import math
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Logger ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | MCP:calculator | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mcp.calculator")

# ── MCP Server ────────────────────────────────────────────────────────────────
server = Server("calculator-server")

_MATH_GLOBALS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
_MATH_GLOBALS.update({"abs": abs, "round": round})


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="calculate",
            description=(
                "Evaluate a safe mathematical expression. "
                "Supports +, -, *, /, **, sqrt, log, sin, cos, abs, round, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate. E.g. '(35 + 30 + 14) / 3'",
                    }
                },
                "required": ["expression"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info("Tool called: %s | args: %s", name, arguments)

    if name != "calculate":
        result = {"error": f"Unknown tool: {name}"}
        logger.warning("Unknown tool: %s", name)
        return [TextContent(type="text", text=json.dumps(result))]

    expression = arguments.get("expression", "").strip()

    if not expression:
        result = {"error": "Empty expression provided."}
        logger.warning("Empty expression")
        return [TextContent(type="text", text=json.dumps(result))]

    try:
        value  = eval(expression, {"__builtins__": {}}, _MATH_GLOBALS)  # noqa: S307
        result = {"expression": expression, "result": float(value)}
        logger.info("Calculated: %s = %s", expression, value)
    except Exception as exc:
        result = {"expression": expression, "error": str(exc)}
        logger.error("Calculation error: %s | %s", expression, exc)

    return [TextContent(type="text", text=json.dumps(result))]


async def main():
    logger.info("Calculator MCP server starting (stdio transport)")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
