"""
A2A Base Service

Every agent (weather, calculator, search) inherits this base and gets:
  - GET  /.well-known/agent.json
  - POST /a2a/task
  - GET  /a2a/task/{task_id}
  - GET  /health
  - Redis task state management
  - Request logging + timing
"""

import time
import logging
from abc import ABC, abstractmethod

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app_ADK.core.a2a_models import A2ATaskRequest, A2ATaskResponse, AgentCard, TaskState
from app_ADK.core.redis_client import set_task, update_task_state, get_task, register_agent_card

logger = logging.getLogger(__name__)


class A2ABaseService(ABC):

    card: AgentCard = None

    @abstractmethod
    async def handle(self, query: str) -> dict:
        ...

    def build_app(self) -> FastAPI:
        app = FastAPI(title=self.card.name)

        @app.on_event("startup")
        async def _startup():
            await register_agent_card(self.card.name, self.card.model_dump())
            logger.info("Agent '%s' started | registered in Redis", self.card.name)

        @app.middleware("http")
        async def _log(request: Request, call_next):
            t0  = time.perf_counter()
            res = await call_next(request)
            ms  = (time.perf_counter() - t0) * 1000
            logger.info("%s %s | %d | %.0fms", request.method, request.url.path, res.status_code, ms)
            return res

        @app.get("/.well-known/agent.json")
        async def agent_card():
            return self.card.model_dump()

        @app.get("/health")
        async def health():
            return {"status": "ok", "agent": self.card.name}

        @app.post("/a2a/task")
        async def a2a_task(req: A2ATaskRequest):
            task_id = req.task_id
            logger.info("Task RECEIVED | id=%s | agent=%s | query=%s",
                        task_id, self.card.name, req.query)

            init = A2ATaskResponse(task_id=task_id, state=TaskState.SUBMITTED)
            await set_task(task_id, init.model_dump())
            await update_task_state(task_id, TaskState.WORKING)

            try:
                result = await self.handle(req.query)
                await update_task_state(task_id, TaskState.COMPLETED, result=result)
                logger.info("Task COMPLETED | id=%s | result=%s", task_id, str(result)[:100])
                return A2ATaskResponse(
                    task_id=task_id,
                    state=TaskState.COMPLETED,
                    result=result,
                ).model_dump()

            except Exception as exc:
                logger.exception("Task FAILED | id=%s | %s", task_id, exc)
                await update_task_state(task_id, TaskState.FAILED, error=str(exc))
                return A2ATaskResponse(
                    task_id=task_id,
                    state=TaskState.FAILED,
                    error=str(exc),
                ).model_dump()

        @app.get("/a2a/task/{task_id}")
        async def get_task_status(task_id: str):
            data = await get_task(task_id)
            if not data:
                return JSONResponse(status_code=404, content={"error": "Task not found"})
            return data

        return app
