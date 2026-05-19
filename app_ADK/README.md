# Google ADK Agent × OpenAI LLM

A conversational AI agent built with **Google Agent Development Kit (ADK)** and powered by **OpenAI GPT models** via LiteLLM.

---

## Project Structure

```
google_adk_agent/
├── agent.py          # Agent definition + tools
├── run.py            # CLI runner (interactive & single-query)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Built-in Tools

| Tool | Description |
|---|---|
| `calculator` | Evaluates math expressions (`sqrt`, `log`, `sin`, `**`, …) |
| `get_weather` | Returns weather for a city (mock data) |
| `search_web` | Simulates a web search and returns ranked results |

---

## Setup

### 1. Clone / copy the project

```bash
cd google_adk_agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your OpenAI API key

```bash
cp .env.example .env
# Edit .env and paste your key
export OPENAI_API_KEY="sk-..."
```

---

## Running the Agent

### Interactive chat (REPL)

```bash
python run.py
```

```
🤖  Google ADK Agent (powered by OpenAI)
    Tools: calculator · weather · web search
    Type 'exit' to quit.

You: What is 2 to the power of 20?
Agent: 2²⁰ equals 1,048,576. I used the calculator tool with the expression "2 ** 20".

You: What's the weather in Tokyo?
Agent: Tokyo is currently 28°C (82.4°F), humid with 85% humidity.

You: exit
Agent: Goodbye! 👋
```

### Single-query mode

```bash
python run.py --query "Calculate the area of a circle with radius 7"
```

### ADK Web UI (built-in)

```bash
adk web
```
Then open `http://localhost:8000` — select **openai_adk_assistant** from the dropdown.

---

## Changing the Model

Edit `agent.py` — swap the model string in `LiteLlm(...)`:

```python
# GPT-4o Mini (fast, cheap — default)
model = LiteLlm(model="openai/gpt-4o-mini")

# GPT-4o (more capable)
model = LiteLlm(model="openai/gpt-4o")

# GPT-4 Turbo
model = LiteLlm(model="openai/gpt-4-turbo")
```

---

## Adding Your Own Tools

1. Write a plain Python function with a docstring (ADK uses it as the tool description).
2. Wrap it with `FunctionTool(your_function)`.
3. Add it to the `tools=[...]` list in `create_agent()`.

```python
def stock_price(ticker: str) -> dict:
    """Return the latest stock price for a ticker symbol."""
    ...

tools=[
    FunctionTool(calculator),
    FunctionTool(get_weather),
    FunctionTool(search_web),
    FunctionTool(stock_price),   # ← new tool
]
```

---

## Key Concepts

| Concept | Role |
|---|---|
| `Agent` | Orchestrates reasoning, tool calls, and replies |
| `LiteLlm` | Bridges Google ADK to any OpenAI-compatible model |
| `FunctionTool` | Wraps a Python function into an ADK tool |
| `Runner` | Manages the event loop, sessions, and streaming |
| `InMemorySessionService` | Stores conversation history in RAM |

---

## Requirements

- Python 3.10+
- OpenAI API key (`OPENAI_API_KEY`)
