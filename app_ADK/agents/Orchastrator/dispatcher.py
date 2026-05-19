"""
Dispatcher — executes a planner-produced plan via A2A HTTP calls.

- Parallel steps run via asyncio.gather()
- Sequential steps wait for dependencies
- $id.field references resolved before each call
- Full structured logging + timing per step
"""

import asyncio
import re
import json
import time
import logging
from typing import Any

from app_ADK.agents.Orchastrator.a2a_client import call_agent
from app_ADK.core.telemetry import span

logger = logging.getLogger(__name__)


async def _resolve_input(raw_input: Any, results: dict) -> str:
    """Resolve $<id>.<field> references. Handles str and dict inputs."""

    def replacer(match):
        step_id = int(match.group(1))
        field   = match.group(2)
        result  = results.get(step_id, {})
        if isinstance(result, dict):
            value = result.get(field, match.group(0))
        else:
            try:
                parsed = json.loads(result)
                value  = parsed.get(field, match.group(0)) if isinstance(parsed, dict) else match.group(0)
            except Exception:
                value = result
        return str(value)

    if isinstance(raw_input, dict):
        resolved = {k: re.sub(r'\$(\d+)\.(\w+)', replacer, str(v)) for k, v in raw_input.items()}
        return next(iter(resolved.values())) if len(resolved) == 1 else json.dumps(resolved)

    return re.sub(r'\$(\d+)\.(\w+)', replacer, str(raw_input))


@span("dispatcher.execute_step")
async def _execute_step(step: dict, results: dict) -> Any:
    """Execute one plan step via A2A HTTP call."""
    sid        = step["id"]
    agent_name = step["agent"]
    raw_input  = step["input"]
    output_key = step.get("output_key", f"step_{sid}")

    resolved = await _resolve_input(raw_input, results)
    logger.info(
        "STEP %02d START | agent=%-20s | key=%-20s | input: %s",
        sid, agent_name, output_key, resolved,
    )

    t0 = time.perf_counter()
    result = await call_agent(agent_name, resolved)
    ms = (time.perf_counter() - t0) * 1000

    if "error" in result:
        logger.error("STEP %02d ERROR | agent=%-20s | %.0fms | %s", sid, agent_name, ms, result["error"])
    else:
        logger.info("STEP %02d DONE  | agent=%-20s | %.0fms", sid, agent_name, ms)

    return result


@span("dispatcher.dispatch")
async def dispatch(plan: dict) -> dict:
    """
    Execute full plan. Returns dict of step_id -> result.
    No longer needs agent_runners — all calls go over A2A HTTP.
    """
    steps     = plan.get("steps", [])
    results   = {}
    completed = set()
    step_map  = {s["id"]: s for s in steps}
    remaining = list(step_map.keys())

    logger.info("DISPATCH START | %d total steps", len(steps))

    while remaining:
        ready = [
            sid for sid in remaining
            if all(dep in completed for dep in step_map[sid].get("depends_on", []))
        ]

        if not ready:
            logger.error("DISPATCH STUCK | steps with unresolvable deps: %s", remaining)
            for sid in remaining:
                results[sid] = {"error": "Unresolved dependencies."}
            break

        logger.info(
            "DISPATCH WAVE | %d step(s) parallel: %s",
            len(ready), ready,
        )

        tasks   = [_execute_step(step_map[sid], results) for sid in ready]
        outputs = await asyncio.gather(*tasks)

        for sid, output in zip(ready, outputs):
            results[sid] = output
            completed.add(sid)
            remaining.remove(sid)

    errors = sum(1 for r in results.values() if "error" in r)
    logger.info(
        "DISPATCH END | %d/%d completed | %d errors",
        len(completed), len(steps), errors,
    )
    return results
