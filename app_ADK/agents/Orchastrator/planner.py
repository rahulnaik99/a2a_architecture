"""
Planner — takes user query + agent cards, returns a structured execution plan.

Output JSON shape:
{
  "steps": [
    {
      "id": 1,
      "agent": "weather_agent",
      "input": "Delhi",
      "depends_on": [],
      "output_key": "delhi_weather"
    },
    {
      "id": 2,
      "agent": "weather_agent",
      "input": "Mumbai",
      "depends_on": [],
      "output_key": "mumbai_weather"
    },
    {
      "id": 3,
      "agent": "calculator_agent",
      "input": "($1.temp_c + $2.temp_c) / 2",
      "depends_on": [1, 2],
      "output_key": "avg_temp"
    }
  ]
}

Rules:
- depends_on: list of step ids whose output this step needs
- input: use $<id>.<field> to reference output fields from previous steps
- Steps with empty depends_on can run in parallel
"""

import json
import re
import litellm


PLANNER_SYSTEM_PROMPT = """
You are a task planning assistant for a multi-agent system.

Given a user query and a list of available agents, produce a JSON execution plan.

--- OUTPUT FORMAT ---
Return ONLY valid JSON, no explanation, no markdown, no backticks.

{
  "steps": [
    {
      "id": <int>,
      "agent": "<agent_name>",
      "input": "<plain string to pass to the agent — never a dict>",
      "depends_on": [<list of step ids this step needs results from>],
      "output_key": "<short snake_case label for this result>"
    }
  ]
}

--- RULES ---
1. Steps with no dependencies (depends_on: []) CAN run in parallel — group them together.
2. Steps that need results from earlier steps MUST list those step ids in depends_on.
3. "input" must ALWAYS be a plain string, never a JSON object or dict.
4. For dependent steps, use $<id>.<field> syntax to reference a specific field
   from a previous step's output. Example: "($1.temp_c + $2.temp_c) / 2"
4. Break multi-entity queries into one step per entity (e.g. one weather call per city).
5. Only use agents from the provided list.
6. If a step is impossible with available agents, skip it and note it in output_key as "unavailable".

--- EXAMPLES ---

Query: "average temperature of Delhi and Mumbai"
Plan:
{
  "steps": [
    {"id": 1, "agent": "weather_agent", "input": "Delhi",  "depends_on": [], "output_key": "delhi_weather"},
    {"id": 2, "agent": "weather_agent", "input": "Mumbai", "depends_on": [], "output_key": "mumbai_weather"},
    {"id": 3, "agent": "calculator_agent", "input": "($1.temp_c + $2.temp_c) / 2", "depends_on": [1, 2], "output_key": "avg_temp"}
  ]
}

Query: "weather in Tokyo"
Plan:
{
  "steps": [
    {"id": 1, "agent": "weather_agent", "input": "Tokyo", "depends_on": [], "output_key": "tokyo_weather"}
  ]
}

Query: "search for latest AI news and count the results"
Plan:
{
  "steps": [
    {"id": 1, "agent": "search_agent", "input": "latest AI news", "depends_on": [], "output_key": "search_results"},
    {"id": 2, "agent": "calculator_agent", "input": "count results from $1.results", "depends_on": [1], "output_key": "result_count"}
  ]
}
"""


async def create_plan(query: str, agent_cards: list[dict]) -> dict:
    """
    Call the LLM to produce a structured execution plan for the given query.

    Args:
        query:       The user's original query.
        agent_cards: List of agent card dicts with name, description, planner_hint, input_schema.

    Returns:
        Parsed plan dict with a 'steps' list.
    """
    def _card_summary(card: dict) -> str:
        lines = [
            f"- {card['name']}: {card['description']}",
            f"  Hint: {card['planner_hint']}",
            f"  Input schema: {json.dumps(card['input_schema'])}",
        ]
        if "supported_inputs" in card:
            lines.append(f"  Supported inputs: {card['supported_inputs']}")
        return "\n".join(lines)

    agents_summary = "\n\n".join([_card_summary(c) for c in agent_cards])

    user_message = f"""
Available agents:
{agents_summary}

User query: {query}

Produce the execution plan JSON now.
"""

    response = await litellm.acompletion(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()

    # strip markdown fences if model ignores instructions
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()

    plan = json.loads(raw)
    return plan
