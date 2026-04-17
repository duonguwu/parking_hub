# -*- coding: utf-8 -*-
"""Tenant Utils — Business logic for tenant management."""
import logging
from typing import List, Dict, Any

from fastapi import HTTPException
from app.api.tenant.tenant_models import TenantModel
from app.api.shared.tool.convert_object_id import convert_mongo_object_id

logger = logging.getLogger(__name__)


def format_tenant(doc) -> dict:
    if isinstance(doc, dict):
        data = doc
    else:
        data = doc.dump()
    return {
        "id": str(data.get("_id", "")),
        "tenant_id": data.get("tenant_id", ""),
        "name": data.get("name", ""),
        "slug": data.get("slug", ""),
        "type": data.get("type", "garage"),
        "status": data.get("status", ""),
        "owner_user_id": data.get("owner_user_id", ""),
        "contact": data.get("contact", {}),
        "subscription_plan": data.get("subscription_plan", "free"),
        "settings": data.get("settings", {}),
        "created_at": str(data.get("created_at", "")),
    }


async def get_all_tenants(current_user: dict, status_filter: str = None) -> List[dict]:
    try:
        filter_dict = {}
        if status_filter:
            filter_dict["status"] = status_filter
        cursor = TenantModel.find(filter_dict, current_user=current_user)
        docs = await cursor.to_list(length=100)
        return [format_tenant(doc) for doc in docs]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading tenants: {e}")
        raise HTTPException(status_code=500, detail="Failed to load tenants")


async def get_tenant_by_id(tenant_id: str, current_user: dict) -> dict:
    oid = convert_mongo_object_id(tenant_id)
    if not oid:
        raise HTTPException(status_code=400, detail="Invalid tenant ID format")
    try:
        doc = await TenantModel.find_one({"_id": oid}, current_user=current_user)
        if not doc:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return format_tenant(doc)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_tenant(tenant_id: str, update_data: dict, current_user: dict) -> bool:
    return await TenantModel.update_with_tenant_check(
        doc_id=tenant_id,
        update_data=update_data,
        current_user=current_user,
    )
