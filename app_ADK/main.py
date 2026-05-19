"""
Orchestrator — main FastAPI app.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from uuid import uuid4

from app_ADK.logger import setup_logging
from app_ADK.run import run_agent
from app_ADK.agents.Orchastrator.a2a_client import discover_agents
from app_ADK.core.a2a_models import A2ATaskRequest, A2ATaskResponse, AgentCard, AgentSkill, TaskState
from app_ADK.core.redis_client import (
    get_redis, close_redis, set_task, get_task,
    update_task_state, register_agent_card, get_all_agent_cards,
)
from app_ADK.core.config import AGENT_URLS, SERVICE_NAME
from app_ADK.core.telemetry import get_trace_id

setup_logging()
logger = logging.getLogger(__name__)

ORCHESTRATOR_CARD = AgentCard(
    name="orchestrator",
    description="Plans and executes multi-agent tasks using A2A protocol.",
    url="http://localhost:8000",
    skills=[AgentSkill(name="orchestrate", description="Plan and execute complex multi-agent queries")],
    tags=["orchestrator", "planner", "a2a"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_redis()
    logger.info("Redis connected")
    cards = await discover_agents()
    for card in cards:
        await register_agent_card(card["name"], card)
    logger.info("Discovered %d agent(s) on startup", len(cards))
    yield
    await close_redis()
    logger.info("Redis disconnected")


app = FastAPI(title="Multi-Agent A2A Orchestrator", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0  = time.perf_counter()
    res = await call_next(request)
    ms  = (time.perf_counter() - t0) * 1000
    logger.info("%s %s | %d | %.0fms", request.method, request.url.path, res.status_code, ms)
    return res


@app.get("/.well-known/agent.json")
async def orchestrator_card():
    return ORCHESTRATOR_CARD.model_dump()


@app.get("/health")
async def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/agents")
async def list_agents():
    cards = await get_all_agent_cards()
    return {"count": len(cards), "agents": cards}


@app.post("/query")
async def query(q: str):
    logger.info("Query: %s", q)
    try:
        answer = await run_agent(q)
        return {"answer": answer}
    except Exception as exc:
        logger.exception("Query error: %s", q)
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.post("/a2a/task", response_model=A2ATaskResponse)
async def a2a_task(req: A2ATaskRequest, background_tasks: BackgroundTasks):
    task_id = req.task_id
    init    = A2ATaskResponse(task_id=task_id, state=TaskState.SUBMITTED)
    await set_task(task_id, init.model_dump())
    logger.info("A2A task submitted | id=%s | query=%s", task_id, req.query)

    async def _process():
        await update_task_state(task_id, TaskState.WORKING)
        try:
            answer = await run_agent(req.query)
            await update_task_state(task_id, TaskState.COMPLETED, result={"answer": answer})
        except Exception as exc:
            await update_task_state(task_id, TaskState.FAILED, error=str(exc))

    background_tasks.add_task(_process)
    return init


@app.get("/a2a/task/{task_id}")
async def get_task_status(task_id: str):
    data = await get_task(task_id)
    if not data:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return data
