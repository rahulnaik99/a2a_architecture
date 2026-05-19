"""
A2A Client — calls agent microservices over HTTP.
"""

import logging
import httpx
from uuid import uuid4

from app_ADK.core.a2a_models import A2ATaskRequest, A2ATaskResponse, TaskState
from app_ADK.core.config import AGENT_URLS

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(60.0)


async def call_agent(agent_name: str, query: str) -> dict:
    base_url = AGENT_URLS.get(agent_name)
    if not base_url:
        logger.error("No URL configured for agent: %s", agent_name)
        return {"error": f"Agent '{agent_name}' URL not configured."}

    task     = A2ATaskRequest(task_id=str(uuid4()), query=query)
    endpoint = f"{base_url}/a2a/task"

    logger.info("A2A CALL | agent=%-20s | task_id=%s | query=%s",
                agent_name, task.task_id, query)

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(endpoint, json=task.model_dump())

            # log body on errors before raising
            if resp.status_code >= 400:
                logger.error(
                    "A2A HTTP %d | agent=%s | body=%s",
                    resp.status_code, agent_name, resp.text[:500],
                )
                return {"error": f"Agent returned HTTP {resp.status_code}: {resp.text[:200]}"}

            data     = resp.json()
            response = A2ATaskResponse(**data)

            if response.state == TaskState.COMPLETED:
                logger.info("A2A DONE | agent=%-20s | task_id=%s | result=%s",
                            agent_name, task.task_id, str(response.result)[:100])
                return response.result if isinstance(response.result, dict) else {"result": response.result}
            else:
                logger.error("A2A FAILED | agent=%-20s | error=%s", agent_name, response.error)
                return {"error": response.error or "Agent task failed"}

    except httpx.ConnectError:
        logger.error("A2A CONNECT ERROR | agent=%s not reachable at %s", agent_name, endpoint)
        return {"error": f"Agent '{agent_name}' not reachable at {endpoint}"}
    except Exception as exc:
        logger.exception("A2A ERROR | agent=%s | %s", agent_name, exc)
        return {"error": str(exc)}


async def discover_agents() -> list[dict]:
    cards = []
    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
        for name, url in AGENT_URLS.items():
            try:
                resp = await client.get(f"{url}/.well-known/agent.json")
                if resp.status_code == 200:
                    cards.append(resp.json())
                    logger.info("Discovered: %s @ %s", name, url)
                else:
                    logger.warning("Card fetch failed for %s: HTTP %d", name, resp.status_code)
            except Exception as exc:
                logger.warning("Could not discover agent '%s': %s", name, exc)
    return cards
