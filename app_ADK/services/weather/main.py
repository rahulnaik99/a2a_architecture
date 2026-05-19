"""
Weather Agent — A2A compliant microservice.

Runs on its own port (default 8001).
Backed by the Weather MCP Server via ADK.
"""

import sys
import logging
from pathlib import Path

from app_ADK.core.a2a_base_service import A2ABaseService
from app_ADK.core.a2a_models import AgentCard, AgentSkill
from app_ADK.core.config import LLM_MODEL, AGENT_URLS

logger = logging.getLogger(__name__)

# ── MCP-backed ADK agent setup ─────────────────────────────────────────────────
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from uuid import uuid4
import json, re, asyncio, concurrent.futures

_MCP_SCRIPT = str(Path(__file__).parent.parent.parent / "mcp_servers" / "weather_server.py")

MOCK_DATA = {
    "london":   {"temp_c": 14, "condition": "Cloudy",        "humidity": 78},
    "new york": {"temp_c": 22, "condition": "Sunny",         "humidity": 55},
    "tokyo":    {"temp_c": 28, "condition": "Humid",         "humidity": 85},
    "paris":    {"temp_c": 18, "condition": "Partly Cloudy", "humidity": 65},
    "sydney":   {"temp_c": 20, "condition": "Clear",         "humidity": 60},
    "delhi":    {"temp_c": 35, "condition": "Hot",           "humidity": 40},
    "mumbai":   {"temp_c": 30, "condition": "Humid",         "humidity": 70},
}


def _make_adk_runner():
    agent = Agent(
        name="weather_agent",
        model=LiteLlm(model=LLM_MODEL),
        description="Weather data agent",
        instruction="""
You are a weather assistant. Use the get_weather tool for the city provided.
Respond ONLY with the raw JSON result from the tool.
""",
        tools=[MCPToolset(connection_params=StdioServerParameters(
            command=sys.executable, args=[_MCP_SCRIPT]
        ))],
    )
    session_svc = InMemorySessionService()
    runner = Runner(app_name="_weather_runner", agent=agent, session_service=session_svc)
    return runner, session_svc


_runner, _session_svc = _make_adk_runner()


def _run_sync(city: str) -> dict:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _inner():
        sid = str(uuid4())
        await _session_svc.create_session(app_name="_weather_runner", user_id="svc", session_id=sid)
        msg = types.Content(role="user", parts=[types.Part(text=city)])
        parts = []
        for ev in _runner.run(user_id="svc", session_id=sid, new_message=msg):
            if ev.content and ev.content.parts:
                for p in ev.content.parts:
                    if hasattr(p, "text") and p.text:
                        parts.append(p.text)
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", "\n".join(parts).strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(raw)
        except Exception:
            return {"text": raw}

    try:
        return loop.run_until_complete(_inner())
    finally:
        loop.close()


# ── Service class ─────────────────────────────────────────────────────────────

class WeatherService(A2ABaseService):
    card = AgentCard(
        name="weather_agent",
        description="Retrieves current weather for a city: temperature, humidity, conditions.",
        url=AGENT_URLS["weather_agent"],
        skills=[AgentSkill(name="get_weather", description="Get weather for a city")],
        supported_inputs=["Delhi","Mumbai","London","New York","Tokyo","Paris","Sydney"],
        planner_hint=(
            "Use for weather/temperature queries. Call once per city. "
            "Supported: Delhi, Mumbai, London, New York, Tokyo, Paris, Sydney. "
            "For 'all locations' create one step per city."
        ),
        input_schema={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        tags=["weather", "temperature", "humidity"],
    )

    async def handle(self, query: str) -> dict:
        logger.info("WeatherService.handle | city: %s", query)
        city = query.strip()
        key  = city.lower()

        # fast path: direct mock lookup (no LLM needed for known cities)
        if key in MOCK_DATA:
            d = MOCK_DATA[key]
            return {
                "city":      city.title(),
                "temp_c":    d["temp_c"],
                "temp_f":    round(d["temp_c"] * 9 / 5 + 32, 1),
                "condition": d["condition"],
                "humidity":  d["humidity"],
            }

        # fallback: ADK + MCP
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return await loop.run_in_executor(pool, _run_sync, city)


# ── App ───────────────────────────────────────────────────────────────────────
from app_ADK.logger import setup_logging
setup_logging()
app = WeatherService().build_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.weather.main:app", host="0.0.0.0", port=8001, reload=True)
