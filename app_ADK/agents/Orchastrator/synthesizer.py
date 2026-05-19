"""
Synthesizer — takes the original query, the plan, and all step results,
then produces a final clean human-readable answer via LLM.
"""

import json
import litellm


SYNTHESIZER_SYSTEM_PROMPT = """
You are a response synthesizer for a multi-agent AI system.

You will receive:
1. The original user query
2. The execution plan that was followed (steps + agent names)
3. The result of each step

Your job:
- Combine all results into a single, clear, human-friendly answer.
- Show your working where relevant (e.g. "Delhi: 35°C, Mumbai: 30°C → average: 32.5°C").
- If any step failed or had an error, mention it clearly but still answer using the available data.
- Do NOT expose internal field names like temp_c, output_key, step ids etc.
- Be concise. No unnecessary padding.
"""


async def synthesize(query: str, plan: dict, results: dict) -> str:
    """
    Produce the final answer by synthesizing all step results.

    Args:
        query:   Original user query.
        plan:    The plan dict (with steps list).
        results: Dict of step_id -> result from the dispatcher.

    Returns:
        Final answer string.
    """
    steps = plan.get("steps", [])

    # build a readable summary of each step's result
    steps_summary = []
    for step in steps:
        sid        = step["id"]
        agent      = step["agent"]
        inp        = step["input"]
        output_key = step.get("output_key", f"step_{sid}")
        result     = results.get(sid, "No result")

        steps_summary.append(
            f"Step {sid} [{agent}] input='{inp}' output_key='{output_key}':\n"
            f"{json.dumps(result, indent=2)}"
        )

    user_message = f"""
Original query: {query}

Execution results:
{'=' * 40}
{chr(10).join(steps_summary)}
{'=' * 40}

Now produce the final answer.
"""

    response = await litellm.acompletion(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
