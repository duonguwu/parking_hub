# -*- coding: utf-8 -*-
"""
Common Enums — Standardized Operation and Resource types for API responses.

Usage:
    from app.api.shared.schemas import Operation, Resource

    return api_response(
        operation=Operation.RETRIEVED,
        resource=Resource.ITEMS,
        data=items_data,
    )

Them resource types moi khi tao feature moi.
"""
from enum import Enum


class Operation(str, Enum):
    """Standard CRUD operations."""
    RETRIEVED = "retrieved"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CHECKED = "checked"
    VALIDATED = "validated"
    PROCESSED = "processed"
    SYNCHRONIZED = "synchronized"


class Resource(str, Enum):
    """
    Common resource types.
    Them resource moi khi tao feature moi.

    Convention:
        - Plural (ITEMS) cho list endpoints
        - Singular (ITEM) cho single-item endpoints
    """
    # === Example feature (thay doi cho domain cua ban) ===
    ITEMS = "items"
    ITEM = "item"
    ITEM_CONFIG = "item config"

    # === Admin / Auth ===
    USERS = "users"
    USER = "user"
    ROLES = "roles"
    ROLE = "role"
    STORES = "stores"
    STORE = "store"
    TENANTS = "tenants"
    TENANT = "tenant"
