"""
Calculator Agent — A2A compliant microservice.
Runs on port 8002.
"""

import math
import logging
import asyncio
from app_ADK.core.a2a_base_service import A2ABaseService
from app_ADK.core.a2a_models import AgentCard, AgentSkill
from app_ADK.core.config import AGENT_URLS

logger = logging.getLogger(__name__)

_MATH_GLOBALS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
_MATH_GLOBALS.update({"abs": abs, "round": round})


class CalculatorService(A2ABaseService):
    card = AgentCard(
        name="calculator_agent",
        description="Evaluates mathematical expressions. Handles arithmetic, averages, percentages.",
        url=AGENT_URLS["calculator_agent"],
        skills=[AgentSkill(name="calculate", description="Evaluate a math expression")],
        planner_hint=(
            "Use for any math: averages, sums, percentages, equations. "
            "Pass a plain expression string with real numbers substituted. "
            "Example input: '(35 + 30 + 14) / 3'"
        ),
        input_schema={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
        tags=["math", "calculator", "average", "sum"],
    )

    async def handle(self, query: str) -> dict:
        logger.info("CalculatorService.handle | expression: %s", query)
        expression = query.strip()
        try:
            value  = eval(expression, {"__builtins__": {}}, _MATH_GLOBALS)  # noqa: S307
            result = {"expression": expression, "result": float(value)}
            logger.info("Result: %s = %s", expression, value)
            return result
        except Exception as exc:
            logger.error("Eval error: %s | %s", expression, exc)
            return {"expression": expression, "error": str(exc)}


from app_ADK.logger import setup_logging
setup_logging()
app = CalculatorService().build_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.calculator.main:app", host="0.0.0.0", port=8002, reload=True)
