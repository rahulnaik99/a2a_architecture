"""
Redis client — used for:
  1. Task state storage     (task_id → A2ATaskResponse)
  2. Result caching         (query hash → answer)
  3. Agent card registry    (agent_name → AgentCard)

All keys are namespaced to avoid collisions.
"""

import json
import hashlib
import logging
import redis.asyncio as aioredis
from typing import Any

from app_ADK.core.config import REDIS_URL, REDIS_TTL_SEC

logger = logging.getLogger(__name__)

# ── Key namespaces ─────────────────────────────────────────────────────────────
_NS_TASK   = "a2a:task:"
_NS_CACHE  = "a2a:cache:"
_NS_CARD   = "a2a:card:"

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        logger.info("Redis connected: %s", REDIS_URL)
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis connection closed")


# ── Task state ─────────────────────────────────────────────────────────────────

async def set_task(task_id: str, data: dict, ttl: int = REDIS_TTL_SEC):
    r = await get_redis()
    await r.set(f"{_NS_TASK}{task_id}", json.dumps(data), ex=ttl)
    logger.debug("Task stored: %s | state=%s", task_id, data.get("state"))


async def get_task(task_id: str) -> dict | None:
    r = await get_redis()
    raw = await r.get(f"{_NS_TASK}{task_id}")
    return json.loads(raw) if raw else None


async def update_task_state(task_id: str, state: str, result: Any = None, error: str = None):
    existing = await get_task(task_id) or {}
    existing.update({"state": state})
    if result is not None:
        existing["result"] = result
    if error is not None:
        existing["error"] = error
    if state in ("completed", "failed"):
        from datetime import datetime, timezone
        existing["completed_at"] = datetime.now(timezone.utc).isoformat()
    await set_task(task_id, existing)
    logger.info("Task %s → %s", task_id, state)


# ── Result cache ───────────────────────────────────────────────────────────────

def _cache_key(query: str) -> str:
    h = hashlib.sha256(query.strip().lower().encode()).hexdigest()[:16]
    return f"{_NS_CACHE}{h}"


async def get_cached_answer(query: str) -> str | None:
    r   = await get_redis()
    raw = await r.get(_cache_key(query))
    if raw:
        logger.info("Cache HIT for query: %s", query[:60])
        return raw
    logger.debug("Cache MISS for query: %s", query[:60])
    return None


async def set_cached_answer(query: str, answer: str, ttl: int = REDIS_TTL_SEC):
    r = await get_redis()
    await r.set(_cache_key(query), answer, ex=ttl)
    logger.info("Cache SET for query: %s", query[:60])


# ── Agent card registry ────────────────────────────────────────────────────────

async def register_agent_card(name: str, card: dict):
    r = await get_redis()
    await r.set(f"{_NS_CARD}{name}", json.dumps(card))
    logger.info("Agent card registered in Redis: %s", name)


async def get_all_agent_cards() -> list[dict]:
    r    = await get_redis()
    keys = await r.keys(f"{_NS_CARD}*")
    if not keys:
        return []
    vals = await r.mget(*keys)
    return [json.loads(v) for v in vals if v]
