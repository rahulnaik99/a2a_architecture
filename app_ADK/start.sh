#!/bin/bash
# ─────────────────────────────────────────────────────────────
# start.sh — starts all agent services + orchestrator in one go
# Usage: ./start.sh
# ─────────────────────────────────────────────────────────────

set -e

# colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# trap Ctrl+C — kill all child processes cleanly
cleanup() {
    echo -e "\n${YELLOW}Shutting down all services...${NC}"
    kill $(jobs -p) 2>/dev/null
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   A2A Multi-Agent System — Starting      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"

cd "$PROJECT_ROOT"

# ── Start agent microservices ──────────────────────────────────
echo -e "\n${YELLOW}[1/4] Starting Weather Agent    → http://localhost:8001${NC}"
uvicorn app_ADK.services.weather.main:app \
    --host 0.0.0.0 --port 8001 \
    --log-level warning \
    > "$LOG_DIR/weather.log" 2>&1 &

echo -e "${YELLOW}[2/4] Starting Calculator Agent → http://localhost:8002${NC}"
uvicorn app_ADK.services.calculator.main:app \
    --host 0.0.0.0 --port 8002 \
    --log-level warning \
    > "$LOG_DIR/calculator.log" 2>&1 &

echo -e "${YELLOW}[3/4] Starting Search Agent     → http://localhost:8003${NC}"
uvicorn app_ADK.services.websearch.main:app \
    --host 0.0.0.0 --port 8003 \
    --log-level warning \
    > "$LOG_DIR/search.log" 2>&1 &

# ── Wait for all 3 agents to be healthy ───────────────────────
echo -e "\n${YELLOW}Waiting for agents to be ready...${NC}"

wait_for() {
    local name=$1
    local url=$2
    local retries=20
    until curl -sf "$url/health" > /dev/null 2>&1; do
        retries=$((retries - 1))
        if [ $retries -eq 0 ]; then
            echo -e "${RED}✗ $name failed to start. Check logs/$name.log${NC}"
            cleanup
        fi
        sleep 0.5
    done
    echo -e "${GREEN}✓ $name is ready${NC}"
}

wait_for "weather    " "http://localhost:8001"
wait_for "calculator " "http://localhost:8002"
wait_for "search     " "http://localhost:8003"

# ── Start orchestrator (foreground — logs go to stdout) ────────
echo -e "\n${YELLOW}[4/4] Starting Orchestrator     → http://localhost:8000${NC}"
echo -e "${GREEN}─────────────────────────────────────────────${NC}"
echo -e "${GREEN}  Docs:    http://localhost:8000/docs${NC}"
echo -e "${GREEN}  Agents:  http://localhost:8000/agents${NC}"
echo -e "${GREEN}  Query:   POST http://localhost:8000/query?q=...${NC}"
echo -e "${GREEN}─────────────────────────────────────────────${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop everything${NC}\n"

uvicorn app_ADK.main:app \
    --host 0.0.0.0 --port 8000 \
    --reload
