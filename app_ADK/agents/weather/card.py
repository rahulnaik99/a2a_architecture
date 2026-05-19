"""
agents/weather/card.py
"""

AGENT_CARD = {
    "name": "weather_agent",
    "version": "1.0.0",
    "owner": "rahul",
    "description": (
        "Retrieves weather information (temperature, humidity, conditions) "
        "for supported cities."
    ),

    "tags": ["weather", "forecast", "temperature", "humidity", "climate"],

    "capabilities": [
        "current weather lookup",
        "temperature retrieval",
        "humidity retrieval",
        "weather condition reporting",
    ],

    "routing_keywords": [
        "weather", "temperature", "forecast",
        "humidity", "rain", "hot", "cold", "climate",
    ],

    # ── SUPPORTED CITIES — planner uses this to know what to ask ──────
    "supported_inputs": [
        "Delhi", "Mumbai", "London", "New York", "Tokyo", "Paris", "Sydney"
    ],

    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": (
                    "City name. Must be one of: "
                    "Delhi, Mumbai, London, New York, Tokyo, Paris, Sydney"
                ),
            }
        },
        "required": ["city"],
    },

    "output_schema": {
        "type": "object",
        "properties": {
            "city":      {"type": "string"},
            "temp_c":    {"type": "number"},
            "temp_f":    {"type": "number"},
            "humidity":  {"type": "integer"},
            "condition": {"type": "string"},
        },
    },

    "examples": [
        {
            "input": "Delhi",
            "output": {"city": "Delhi", "temp_c": 35, "humidity": 40, "condition": "Hot"},
        },
        {
            "input": "Mumbai",
            "output": {"city": "Mumbai", "temp_c": 30, "humidity": 70, "condition": "Humid"},
        },
    ],

    "planner_hint": (
        "Use this agent for weather, temperature, humidity, or climate queries. "
        "Call it once per city. "
        "Supported cities: Delhi, Mumbai, London, New York, Tokyo, Paris, Sydney. "
        "If the user says 'all locations', create one step per supported city."
    ),

    "supports_parallel_execution": True,
    "supports_streaming": False,
    "average_latency_ms": 300,
    "dependencies": [],
    "limitations": [
        "Only supports: Delhi, Mumbai, London, New York, Tokyo, Paris, Sydney",
        "Does not provide real-time weather data",
    ],
}
