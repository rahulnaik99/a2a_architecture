"""
run.py — adds app_ADK/ to sys.path so 'core' is importable,
then delegates to the orchestrator.
"""
import sys
from pathlib import Path

# Ensure the app_ADK package root (where core/ lives) is on sys.path
_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv()

from app_ADK.agents.Orchastrator.agent import run_orchestrator


async def run_agent(query: str) -> str:
    return await run_orchestrator(query)
