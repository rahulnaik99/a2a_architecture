# Search Agent

## Purpose

Retrieves web/internet information.

---

## Capabilities

- Web search
- General information retrieval
- Internet lookup
- Latest information search
- Search summarization

---

## Input Format

```json
{
  "query": "latest AI news"
}
```

---

## Output Format

```json
{
  "query": "latest AI news",
  "results": [
    {
      "title": "AI News",
      "snippet": "Latest developments in AI",
      "url": "https://example.com"
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
  "query": "who is Alan Turing"
}
```

Output:

```json
{
  "results": [
    {
      "title": "Alan Turing",
      "snippet": "Computer scientist and mathematician"
    }
  ]
}
```

---

### Example 2

Input:

```json
{
  "query": "latest AI news"
}
```

Output:

```json
{
  "results": [
    {
      "title": "AI News",
      "snippet": "Latest developments in AI"
    }
  ]
}
```

---

## Planner Guidance

Use this agent whenever:
- internet search is required
- latest information is needed
- factual/general lookup is requested

---

## Limitations

- Search results may be mocked
- Real-time accuracy is not guaranteed