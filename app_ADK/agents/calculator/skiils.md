# Calculator Agent

## Purpose

Performs mathematical calculations and equation solving.

---

## Capabilities

- Arithmetic
- Average calculations
- Scientific calculations
- Equation solving
- Numerical aggregation

---

## Input Format

```json
{
  "expression": "2 + 5 * 10"
}
```

---

## Output Format

```json
{
  "result": 52
}
```

---

## Examples

### Example 1

Input:

```json
{
  "expression": "2 + 5 * 10"
}
```

Output:

```json
{
  "result": 52
}
```

---

### Example 2

Input:

```json
{
  "expression": "average(35,30,33)"
}
```

Output:

```json
{
  "result": 32.6
}
```

---

## Planner Guidance

Use this agent whenever:
- calculations are required
- averages must be computed
- equations need solving
- mathematical reasoning is needed

---

## Limitations

- Only supports safe expressions
- Does not execute arbitrary Python code