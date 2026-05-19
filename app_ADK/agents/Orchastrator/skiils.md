# Orchestrator Agent

## Purpose

Plans and coordinates multi-agent workflows.

---

## Capabilities

- Task decomposition
- Multi-step planning
- Agent selection
- Workflow orchestration
- Sequential execution planning
- Multi-agent chaining

---

## Input Format

```json
{
  "query": "Average temperature of Delhi and Mumbai"
}
```

---

## Output Format

```json
{
  "steps": [
    {
      "agent": "weather_agent",
      "input": "Delhi"
    },
    {
      "agent": "weather_agent",
      "input": "Mumbai"
    },
    {
      "agent": "calculator_agent",
      "input": "average(35,30)"
    }
  ]
}
```

---

## Examples

### Example 1

Input:

```json
{
  "query": "Weather in Delhi"
}
```

Output:

```json
{
  "steps": [
    {
      "agent": "weather_agent",
      "input": "Delhi"
    }
  ]
}
```

---

### Example 2

Input:

```json
{
  "query": "Average temperature of Delhi and Mumbai"
}
```

Output:

```json
{
  "steps": [
    {
      "agent": "weather_agent",
      "input": "Delhi"
    },
    {
      "agent": "weather_agent",
      "input": "Mumbai"
    },
    {
      "agent": "calculator_agent",
      "input": "average(35,30)"
    }
  ]
}
```

---

## Planner Guidance

- Break large tasks into smaller executable steps
- Select the correct agent for each step
- Chain outputs between agents
- Return ONLY structured JSON

---

## Limitations

- Depends on available agents
- Cannot execute unsupported capabilities