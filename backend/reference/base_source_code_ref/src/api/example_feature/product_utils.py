# -*- coding: utf-8 -*-
"""
Product Utils — Business logic cho product operations.

Quy tac:
    - TAT CA validation o day (khong o views)
    - Handle tat ca exceptions va convert thanh HTTPException
    - Logging errors
    - Type hints day du
    - KHONG import FastAPI dependencies (Request, Depends, etc.)
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from app.api.example_feature.product_models import ProductModel
from app.api.shared.common_utils import validate_id_format


async def get_all_products(
    current_user: dict,
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Lay danh sach products (voi tenant filter tu dong).

    Args:
        current_user: User dict tu Depends(get_current_user)
        category:     Optional filter theo category

    Returns:
        List[Dict]: Danh sach products
    """
    try:
        filter_dict = {}
        if category:
            filter_dict["category"] = category

        cursor = ProductModel.find(filter_dict, current_user=current_user).sort("name", 1)
        docs = await cursor.to_list(length=None)

        return [_format_product(doc) for doc in docs]

    except Exception as e:
        print(f"Error loading products: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load products: {e}")


async def get_product_by_id(
    product_id: str,
    current_user: dict,
) -> Dict[str, Any]:
    """
    Lay product theo ID.

    Args:
        product_id:   MongoDB ObjectId string
        current_user: User dict

    Returns:
        Dict: Product data

    Raises:
        HTTPException 400: Invalid ID format
        HTTPException 404: Product not found
    """
    doc = await ProductModel.get_by_id_with_tenant_check(
        doc_id=product_id,
        current_user=current_user,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    return _format_product(doc)


async def create_product(
    data: dict,
    current_user: dict,
) -> Dict[str, Any]:
    """
    Tao product moi.

    Args:
        data:         Request data (tu schema.model_dump())
        current_user: User dict

    Returns:
        Dict: Created product data

    Raises:
        HTTPException 400: Validation error hoac name trung trong tenant
    """
    target_tenant_id = data.pop("target_tenant_id", None)

    try:
        doc = await ProductModel.create_with_tenant_check(
            data_dict=data,
            current_user=current_user,
            name_field="name",
            target_tenant_id=target_tenant_id,
        )

        return _format_product(doc)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create product: {e}")


async def update_product(
    product_id: str,
    update_data: dict,
    current_user: dict,
) -> bool:
    """
    Cap nhat product.

    Args:
        product_id:   MongoDB ObjectId string
        update_data:  Fields can update (tu schema.model_dump(exclude_unset=True))
        current_user: User dict

    Returns:
        bool: True neu update thanh cong
    """
    try:
        updated = await ProductModel.update_with_tenant_check(
            doc_id=product_id,
            update_data=update_data,
            current_user=current_user,
            name_field="name",
        )
        return updated

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update product: {e}")


async def delete_product(
    product_id: str,
    current_user: dict,
) -> bool:
    """
    Xoa product.

    Args:
        product_id:   MongoDB ObjectId string
        current_user: User dict

    Returns:
        bool: True neu delete thanh cong
    """
    try:
        deleted = await ProductModel.delete_with_tenant_check(
            doc_id=product_id,
            current_user=current_user,
            # check_usage_callback=check_product_in_orders,  # Optional
        )
        return deleted

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {e}")


# ─── Private helpers ─────────────────────────────────────────────

def _format_product(doc) -> Dict[str, Any]:
    """Format MongoDB document thanh dict cho API response."""
    c = doc.dump()
    return {
        "id": str(doc.id),
        "name": c.get("name", ""),
        "description": c.get("description", ""),
        "price": c.get("price", 0),
        "category": c.get("category", "general"),
        "is_active": c.get("is_active", True),
        "tenant_id": c.get("tenant_id", ""),
        "created_at": str(c.get("created_at", "")),
        "updated_at": str(c.get("updated_at", "")),
    }
