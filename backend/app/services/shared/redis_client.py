# -*- coding: utf-8 -*-
"""
Redis Singleton — Async client for caching + distributed locks.

Phase 2 usage:
    - Cache OSM routing results (key: route:{origin_h}:{dest_h}, TTL=1h)
    - Cache weather responses (key: weather:{lat_rounded}:{lng_rounded})
    - Distributed lock for booking creation (prevent double-booking)
    - Session storage for search history
"""
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Singleton wrapper around redis.asyncio."""

    _instance: Optional["RedisClient"] = None
    _redis: Optional[aioredis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        if self._redis is None:
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8",
            )
            try:
                await self._redis.ping()
                logger.info(f"Redis connected: {settings.REDIS_URL}")
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self._redis = None
                raise

    async def disconnect(self) -> None:
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    @property
    def redis(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis

    # ── Key-value ──────────────────────────────────────────────────

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.redis.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        data = json.dumps(value, default=str)
        await self.redis.set(key, data, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    # ── Distributed lock ───────────────────────────────────────────

    @asynccontextmanager
    async def lock_context(self, key: str, timeout: int = None, blocking_timeout: float = 5.0):
        """
        Acquire a distributed lock. Block up to `blocking_timeout` seconds.
        Auto-release on exit. Raises TimeoutError if can't acquire.

        Usage:
            async with redis_client.lock_context("slot:g1:18:30", timeout=10):
                # critical section
                ...
        """
        timeout = timeout or settings.REDIS_LOCK_TIMEOUT_SECONDS
        lock = self.redis.lock(
            name=f"lock:{key}",
            timeout=timeout,
            blocking=True,
            blocking_timeout=blocking_timeout,
        )
        acquired = await lock.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock: {key}")
        try:
            yield lock
        finally:
            try:
                await lock.release()
            except Exception:
                # Lock may have expired — ignore
                pass


# Singleton instance
redis_client = RedisClient()
