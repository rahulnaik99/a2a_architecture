"""
Central config — reads from environment / .env file.
All services import from here.
"""
import os
from dotenv import load_dotenv
load_dotenv()

# LLM
OPENAI_API_KEY   = os.environ.get("OPENAI_API_KEY", "")
LLM_MODEL        = os.environ.get("LLM_MODEL", "openai/gpt-4o-mini")

# BTP AI Core (swap when deploying to SAP BTP)
BTP_AICORE_URL   = os.environ.get("BTP_AICORE_URL", "")
BTP_AICORE_TOKEN = os.environ.get("BTP_AICORE_TOKEN", "")

# Redis
REDIS_URL        = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_TTL_SEC    = int(os.environ.get("REDIS_TTL_SEC", 300))   # 5 min default

# A2A agent registry (service URLs)
AGENT_URLS = {
    "weather_agent":    os.environ.get("WEATHER_AGENT_URL",    "http://localhost:8001"),
    "calculator_agent": os.environ.get("CALCULATOR_AGENT_URL", "http://localhost:8002"),
    "search_agent":     os.environ.get("SEARCH_AGENT_URL",     "http://localhost:8003"),
}

# Observability
OTEL_ENABLED     = os.environ.get("OTEL_ENABLED", "false").lower() == "true"
OTEL_ENDPOINT    = os.environ.get("OTEL_ENDPOINT", "http://localhost:4317")
SERVICE_NAME     = os.environ.get("SERVICE_NAME", "a2a-orchestrator")
