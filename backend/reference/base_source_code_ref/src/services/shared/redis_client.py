# -*- coding: utf-8 -*-
"""
Redis Client — Singleton with dual connection pools.

Dual pools:
    - Text pool  (decode_responses=True):  JSON data, stats, config, pub/sub
    - Binary pool (decode_responses=False): Binary data (files, images, frames)

Usage:
    from app.services.shared.redis_client import redis_client

    # Trong startup
    await redis_client.connect()

    # Operations
    await redis_client.set_stats("item_123", {"count": 42})
    stats = await redis_client.get_stats("item_123")

    await redis_client.publish("channel:updates", {"action": "created"})

    async with redis_client.lock_context("process_item"):
        await do_critical_work()

    # Trong shutdown
    await redis_client.disconnect()
"""
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio import ConnectionPool
from redis.asyncio.lock import Lock

from .abstractions.singleton import SingletonClass

logger = logging.getLogger(__name__)


class RedisClient(SingletonClass):
    """Redis client singleton voi dual pools cho text va binary data."""

    def _singleton_init(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 100,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections

        # Pool cho text data (stats, config) — decode_responses=True
        self.text_pool: Optional[ConnectionPool] = None
        self.text_redis: Optional[redis.Redis] = None

        # Pool cho binary data (files, images) — decode_responses=False
        self.binary_pool: Optional[ConnectionPool] = None
        self.binary_redis: Optional[redis.Redis] = None

        self._connected = False

    # ─── Connection lifecycle ────────────────────────────────────

    async def connect(self):
        """Tao ket noi toi Redis voi 2 connection pools."""
        if self._connected:
            return

        try:
            # Text pool
            self.text_pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections // 2,
                encoding="utf-8",
                decode_responses=True,
            )
            self.text_redis = redis.Redis(connection_pool=self.text_pool)

            # Binary pool
            self.binary_pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections // 2,
                decode_responses=False,
            )
            self.binary_redis = redis.Redis(connection_pool=self.binary_pool)

            # Test connections
            await self.text_redis.ping()
            await self.binary_redis.ping()

            self._connected = True
            logger.info(f"Redis connected: {self.host}:{self.port}/{self.db}")

        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def disconnect(self):
        """Dong tat ca connections."""
        if self.text_redis:
            await self.text_redis.close()
        if self.binary_redis:
            await self.binary_redis.close()
        if self.text_pool:
            await self.text_pool.disconnect()
        if self.binary_pool:
            await self.binary_pool.disconnect()

        self._connected = False
        logger.info("Redis disconnected")

    def _ensure_connected(func):
        """Decorator dam bao Redis da connect truoc khi goi method."""
        async def wrapper(self, *args, **kwargs):
            if not self._connected:
                await self.connect()
            return await func(self, *args, **kwargs)
        return wrapper

    # ─── Binary data operations ──────────────────────────────────

    @_ensure_connected
    async def set_binary(self, key: str, data: bytes, ttl: int = 60):
        """Luu binary data (files, images, etc.)."""
        await self.binary_redis.set(key, data, ex=ttl)

    @_ensure_connected
    async def get_binary(self, key: str) -> Optional[bytes]:
        """Doc binary data."""
        return await self.binary_redis.get(key)

    @_ensure_connected
    async def get_binary_batch(self, keys: List[str]) -> List[Optional[bytes]]:
        """Doc nhieu binary data cung luc (pipeline)."""
        return await self.binary_redis.mget(keys)

    # ─── Text/JSON operations ────────────────────────────────────

    @_ensure_connected
    async def set_stats(self, key: str, stats: Dict, ttl: int = 30):
        """Luu JSON data vao Redis."""
        import json
        await self.text_redis.set(f"stats:{key}", json.dumps(stats), ex=ttl)

    @_ensure_connected
    async def get_stats(self, key: str) -> Optional[Dict]:
        """Doc JSON data tu Redis."""
        import json
        data = await self.text_redis.get(f"stats:{key}")
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in stats:{key}")
        return None

    @_ensure_connected
    async def set_text(self, key: str, value: str, ttl: Optional[int] = None):
        """Luu text data."""
        await self.text_redis.set(key, value, ex=ttl)

    @_ensure_connected
    async def get_text(self, key: str) -> Optional[str]:
        """Doc text data."""
        return await self.text_redis.get(key)

    # ─── Pub/Sub ─────────────────────────────────────────────────

    @_ensure_connected
    async def publish(self, channel: str, message: Union[str, Dict]):
        """Publish message toi Redis Pub/Sub channel."""
        import json
        if isinstance(message, dict):
            message = json.dumps(message)
        await self.text_redis.publish(channel, message)

    @_ensure_connected
    async def subscribe(self, *channels: str):
        """
        Subscribe toi Redis Pub/Sub channels.

        Returns:
            PubSub object de listen messages

        Usage:
            pubsub = await redis_client.subscribe("channel:updates")
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
        """
        pubsub = self.text_redis.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub

    # ─── Utility operations ──────────────────────────────────────

    @asynccontextmanager
    async def lock_context(self, name: str, timeout: int = 10, blocking_timeout: int = 5):
        """
        Redis distributed lock context manager.

        Usage:
            async with redis_client.lock_context("process_item_123"):
                await do_critical_work()
        """
        if not self._connected:
            await self.connect()

        lock: Lock = self.text_redis.lock(
            name=f"lock:{name}",
            timeout=timeout,
            blocking_timeout=blocking_timeout,
        )

        acquired = await lock.acquire()
        if not acquired:
            raise Exception(f"Cannot acquire lock: {name}")

        try:
            yield
        finally:
            await lock.release()

    @_ensure_connected
    async def delete_keys(self, pattern: str) -> int:
        """Xoa keys theo pattern (vd: "stats:*")."""
        keys = []
        async for key in self.text_redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.text_redis.delete(*keys)
        return len(keys)

    @_ensure_connected
    async def health_check(self) -> bool:
        """Kiem tra Redis connection health."""
        try:
            await self.text_redis.ping()
            await self.binary_redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# ── Global singleton instance ────────────────────────────────────
redis_client = RedisClient()
