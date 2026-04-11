# -*- coding: utf-8 -*-
"""
Product Views — API endpoints cho product management.

Quy tac:
    - SIEU NGAN GON: 2-4 lines per endpoint
    - KHONG validation: de utils handle
    - KHONG try-catch: utils da handle exceptions
    - Su dung api_response(): standardized response format
    - KHONG business logic: chi HTTP handling
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional

from app.api.example_feature.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.api.example_feature.product_utils import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
)
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import has_permission

# Router — tags cho OpenAPI grouping
product_router = APIRouter(tags=["product management"])


@product_router.get("/products")
@has_permission(["product:view"])
async def get_products(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lay danh sach products."""
    data = await get_all_products(current_user=current_user, category=category)
    return api_response(Operation.RETRIEVED, Resource.ITEMS, data)


@product_router.get("/products/{product_id}")
@has_permission(["product:view"])
async def get_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Lay product theo ID."""
    data = await get_product_by_id(product_id, current_user=current_user)
    return api_response(Operation.RETRIEVED, Resource.ITEM, data)


@product_router.post("/products")
@has_permission(["product:create"])
async def create_product_endpoint(
    request: ProductCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Tao product moi."""
    data = await create_product(request.model_dump(), current_user=current_user)
    return api_response(Operation.CREATED, Resource.ITEM, data)


@product_router.put("/products/{product_id}")
@has_permission(["product:edit"])
async def update_product_endpoint(
    product_id: str,
    request: ProductUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Cap nhat product."""
    await update_product(product_id, request.model_dump(exclude_unset=True), current_user=current_user)
    return api_response(Operation.UPDATED, Resource.ITEM)


@product_router.delete("/products/{product_id}")
@has_permission(["product:delete"])
async def delete_product_endpoint(
    product_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Xoa product."""
    await delete_product(product_id, current_user=current_user)
    return api_response(Operation.DELETED, Resource.ITEM)
