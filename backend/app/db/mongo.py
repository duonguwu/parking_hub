# -*- coding: utf-8 -*-
"""
MongoDB Connection — Motor (async) + Umongo (ODM) singleton.

Usage:
    from app.db.mongo import mongo_instance, init_mongo, close_mongo
"""
import logging
from typing import Optional
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks import MotorAsyncIOInstance

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Singleton Umongo Instance ────────────────────────────────────
mongo_instance = MotorAsyncIOInstance()
_motor_client: Optional[AsyncIOMotorClient] = None


def get_motor_client() -> AsyncIOMotorClient:
    """Get the async motor client instance."""
    if _motor_client is None:
        raise RuntimeError("MongoDB client not initialized. Call init_mongo() first.")
    return _motor_client


def init_mongo() -> MotorAsyncIOInstance:
    """
    Initialize Async MongoDB client and bind to Umongo instance.
    Called once on app startup (lifespan).
    """
    global _motor_client

    if _motor_client is None:
        _motor_client = AsyncIOMotorClient(settings.MONGO_URI)
        _motor_client.get_io_loop = asyncio.get_running_loop

        db = _motor_client[settings.MONGO_DB]
        mongo_instance.set_db(db)

        logger.info(f"Motor & Umongo initialized for db: {settings.MONGO_DB}")

    return mongo_instance


def close_mongo():
    """Close the MongoDB client (call on shutdown)."""
    global _motor_client
    if _motor_client:
        _motor_client.close()
        _motor_client = None
        logger.info("MongoDB Async Client closed")
