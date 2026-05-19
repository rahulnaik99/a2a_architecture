"""
Orchestrator Service — A2A compliant, Redis-cached, OTEL-traced.

Flow:
  1. Check Redis cache → return instantly if hit
  2. Discover agent cards (from Redis or /.well-known/agent.json)
  3. Planner → JSON plan
  4. Dispatcher → A2A HTTP calls (parallel + sequential)
  5. Synthesizer → final answer
  6. Cache answer in Redis
"""

import json
import time
import logging

from app_ADK.agents.Orchastrator.planner     import create_plan
from app_ADK.agents.Orchastrator.dispatcher  import dispatch
from app_ADK.agents.Orchastrator.synthesizer import synthesize
from app_ADK.agents.Orchastrator.a2a_client  import discover_agents
from app_ADK.core.redis_client import (
    get_cached_answer, set_cached_answer,
    get_all_agent_cards, register_agent_card,
)
from app_ADK.core.telemetry import span, get_trace_id

logger = logging.getLogger(__name__)


@span("orchestrator.run")
async def run_orchestrator(query: str) -> str:
    t_total = time.perf_counter()
    trace   = get_trace_id()
    logger.info("=" * 70)
    logger.info("ORCHESTRATOR START | trace=%s | query: %s", trace, query)

    # ── 1. Cache check ─────────────────────────────────────────────────────
    cached = await get_cached_answer(query)
    if cached:
        logger.info("CACHE HIT | returning immediately | trace=%s", trace)
        logger.info("=" * 70)
        return cached

    # ── 2. Agent card discovery ────────────────────────────────────────────
    # Try Redis first (fast), fallback to live HTTP discovery
    agent_cards = await get_all_agent_cards()
    if not agent_cards:
        logger.info("No cards in Redis — discovering from agent services...")
        agent_cards = await discover_agents()
        for card in agent_cards:
            await register_agent_card(card["name"], card)

    if not agent_cards:
        logger.error("No agent cards available — cannot plan")
        return "No agents available to handle this query."

    logger.info("Using %d agent(s): %s", len(agent_cards), [c["name"] for c in agent_cards])

    # ── 3. Plan ───────────────────────────────────────────────────────────
    t0   = time.perf_counter()
    plan = await create_plan(query, agent_cards)
    logger.info(
        "PLANNER | %.0fms | %d steps",
        (time.perf_counter() - t0) * 1000,
        len(plan.get("steps", [])),
    )
    logger.debug("Plan:\n%s", json.dumps(plan, indent=2))

    # ── 4. Dispatch ───────────────────────────────────────────────────────
    t0      = time.perf_counter()
    results = await dispatch(plan)
    logger.info(
        "DISPATCHER | %.0fms | %d results",
        (time.perf_counter() - t0) * 1000,
        len(results),
    )

    # ── 5. Synthesize ─────────────────────────────────────────────────────
    t0     = time.perf_counter()
    answer = await synthesize(query, plan, results)
    logger.info("SYNTHESIZER | %.0fms", (time.perf_counter() - t0) * 1000)

    # ── 6. Cache result ───────────────────────────────────────────────────
    await set_cached_answer(query, answer)

    logger.info(
        "ORCHESTRATOR END | total=%.0fms | trace=%s",
        (time.perf_counter() - t_total) * 1000, trace,
    )
    logger.info("=" * 70)
    return answer


def create_orchestrator():
    return None
