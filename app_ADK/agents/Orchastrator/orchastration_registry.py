"""
Auto-discovery registry.

Scans the agents/ directory for any package that exposes:
  - create_agent() -> Agent
  - AGENT_CARD     -> dict

No manual registration needed. Drop a new agent folder in — it's picked up automatically.
"""

import importlib
import importlib.util
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_AGENTS_ROOT = Path(__file__).parent.parent   # .../app_ADK/agents/
_SKIP        = {"Orchastrator", "__pycache__"}


def _discover() -> tuple[dict, list]:
    registry: dict = {}
    cards:    list = []

    for agent_dir in sorted(_AGENTS_ROOT.iterdir()):
        if not agent_dir.is_dir():
            continue
        if agent_dir.name in _SKIP or agent_dir.name.startswith("_"):
            continue

        # find the main agent file (not __init__.py or card.py)
        candidate = None
        for f in sorted(agent_dir.glob("*.py")):
            if f.name not in ("__init__.py", "card.py"):
                candidate = f
                break

        card_file = agent_dir / "card.py"

        if candidate is None or not card_file.exists():
            continue

        # load via spec so we don't depend on sys.path or package structure
        agent_name_key = agent_dir.name  # used only for logging

        try:
            agent_spec  = importlib.util.spec_from_file_location(
                f"_agent_{agent_dir.name}", candidate
            )
            agent_mod   = importlib.util.module_from_spec(agent_spec)
            agent_spec.loader.exec_module(agent_mod)

            card_spec   = importlib.util.spec_from_file_location(
                f"_card_{agent_dir.name}", card_file
            )
            card_mod    = importlib.util.module_from_spec(card_spec)
            card_spec.loader.exec_module(card_mod)

        except Exception as exc:
            logger.warning("Skipping agent folder '%s': import error — %s", agent_name_key, exc)
            continue

        if not hasattr(agent_mod, "create_agent"):
            logger.warning("Skipping '%s': no create_agent() found.", candidate)
            continue
        if not hasattr(card_mod, "AGENT_CARD"):
            logger.warning("Skipping '%s': no AGENT_CARD found.", card_file)
            continue

        card       = card_mod.AGENT_CARD
        agent_name = card["name"]

        try:
            registry[agent_name] = agent_mod.create_agent()
            cards.append(card)
            logger.info("Registered agent: %s  (from %s)", agent_name, candidate.name)
        except Exception as exc:
            logger.warning("Failed to instantiate agent '%s': %s", agent_name, exc)

    return registry, cards


AGENT_REGISTRY, AGENT_CARDS = _discover()
