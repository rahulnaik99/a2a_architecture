# Weather Agent

## Purpose

Provides weather information for cities.

---

## Capabilities

- Current temperature
- Humidity
- Weather condition
- Climate lookup

---

## Input Format

```json
{
  "city": "Delhi"
}
```

---

## Output Format

```json
{
  "city": "Delhi",
  "temp_c": 35,
  "humidity": 40,
  "condition": "Hot"
}
```

---

## Examples

### Example 1

Input:

```json
{
  "city": "Delhi"
}
```

Output:

```json
{
  "city": "Delhi",
  "temp_c": 35,
  "humidity": 40,
  "condition": "Hot"
}
```

---

### Example 2

Input:

```json
{
  "city": "Mumbai"
}
```

Output:

```json
{
  "city": "Mumbai",
  "temp_c": 30,
  "humidity": 70,
  "condition": "Humid"
}
```

---

## Planner Guidance

Use this agent whenever:
- weather data is required
- temperature is requested
- humidity is requested
- climate/forecast information is needed

---

## Limitations

- Supports only predefined cities
- Does not provide real-time weather