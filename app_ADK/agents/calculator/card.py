"""
agents/calculator/card.py
"""

AGENT_CARD = {
    # ── Identity ──────────────────────────────────────────────────────
    "name": "calculator_agent",
    "version": "1.0.0",
    "owner": "rahul",
    "description": (
        "Specialized agent for performing mathematical "
        "calculations and equation solving."
    ),

    # ── Discovery Metadata ────────────────────────────────────────────
    "tags": [
        "math",
        "calculator",
        "equation",
        "arithmetic",
        "statistics",
    ],

    "capabilities": [
        "basic arithmetic",
        "scientific calculations",
        "average calculations",
        "equation solving",
        "mathematical reasoning",
    ],

    # ── Routing Hints ─────────────────────────────────────────────────
    "routing_keywords": [
        "calculate",
        "math",
        "average",
        "sum",
        "multiply",
        "divide",
        "equation",
        "formula",
    ],

    # ── Input / Output Schema ─────────────────────────────────────────
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression",
            }
        },
        "required": ["expression"],
    },

    "output_schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "number",
            }
        },
    },

    # ── Examples ──────────────────────────────────────────────────────
    "examples": [
        {
            "input": "2 + 5 * 10",
            "output": {
                "result": 52
            },
        },
        {
            "input": "average(35,30,33)",
            "output": {
                "result": 32.6
            },
        },
    ],

    # ── Planner Guidance ──────────────────────────────────────────────
    "planner_hint": (
        "Use this agent whenever mathematical calculations, "
        "averages, equations, or arithmetic operations are needed."
    ),

    # ── Executor Metadata ─────────────────────────────────────────────
    "supports_parallel_execution": True,
    "supports_streaming": False,
    "average_latency_ms": 150,

    # ── Dependency Metadata ───────────────────────────────────────────
    "dependencies": [],

    # ── Safety / Limits ───────────────────────────────────────────────
    "limitations": [
        "Does not execute arbitrary Python code",
        "Only supports safe mathematical expressions",
    ],
}