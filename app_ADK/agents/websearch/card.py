"""
agents/search/card.py
"""

AGENT_CARD = {
    # ── Identity ──────────────────────────────────────────────────────
    "name": "search_agent",
    "version": "1.0.0",
    "owner": "rahul",
    "description": (
        "Specialized agent for searching and retrieving "
        "general web/internet information."
    ),

    # ── Discovery Metadata ────────────────────────────────────────────
    "tags": [
        "search",
        "web",
        "internet",
        "knowledge",
        "information",
    ],

    "capabilities": [
        "web search",
        "internet lookup",
        "general knowledge retrieval",
        "latest information retrieval",
        "search summarization",
    ],

    # ── Routing Hints ─────────────────────────────────────────────────
    "routing_keywords": [
        "search",
        "find",
        "lookup",
        "internet",
        "latest",
        "information",
        "who is",
        "what is",
    ],

    # ── Input / Output Schema ─────────────────────────────────────────
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
            }
        },
        "required": ["query"],
    },

    "output_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
            },
            "results": {
                "type": "array",
            },
        },
    },

    # ── Examples ──────────────────────────────────────────────────────
    "examples": [
        {
            "input": "latest AI news",
            "output": {
                "results": [
                    {
                        "title": "AI News",
                        "snippet": "Latest AI developments",
                    }
                ]
            },
        },
        {
            "input": "who is Alan Turing",
            "output": {
                "results": [
                    {
                        "title": "Alan Turing",
                        "snippet": "Computer scientist",
                    }
                ]
            },
        },
    ],

    # ── Planner Guidance ──────────────────────────────────────────────
    "planner_hint": (
        "Use this agent whenever internet search, "
        "general information lookup, or latest information is required."
    ),

    # ── Executor Metadata ─────────────────────────────────────────────
    "supports_parallel_execution": True,
    "supports_streaming": True,
    "average_latency_ms": 800,

    # ── Dependency Metadata ───────────────────────────────────────────
    "dependencies": [],

    # ── Safety / Limits ───────────────────────────────────────────────
    "limitations": [
        "Search results may be simulated/mock data",
        "Does not guarantee real-time accuracy",
    ],
}