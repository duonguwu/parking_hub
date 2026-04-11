# -*- coding: utf-8 -*-
"""
Product API Schemas — Request/Response models cho product endpoints.

Quy tac:
    - Dung Field() voi description va validation
    - Tach rieng Request va Response schemas
    - Validation constraints (ge=0, min_length, etc.)
    - Optional fields cho Update requests
    - KHONG de logic business trong schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


# ─── Request Schemas ─────────────────────────────────────────────

class ProductCreateRequest(BaseModel):
    """Schema cho tao product moi."""
    name: str = Field(..., description="Ten product", min_length=1, max_length=200)
    description: str = Field("", description="Mo ta product", max_length=1000)
    price: float = Field(..., description="Gia product", ge=0)
    category: str = Field("general", description="Danh muc")
    target_tenant_id: Optional[str] = Field(
        None,
        description="Tenant ID dich (chi super_admin/center manager dung)",
    )


class ProductUpdateRequest(BaseModel):
    """Schema cho cap nhat product. Chi gui fields can thay doi."""
    name: Optional[str] = Field(None, description="Ten product", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Mo ta product", max_length=1000)
    price: Optional[float] = Field(None, description="Gia product", ge=0)
    category: Optional[str] = Field(None, description="Danh muc")
    is_active: Optional[bool] = Field(None, description="Trang thai active")


# ─── Response Schemas (optional, dung khi can custom format) ─────

class ProductResponse(BaseModel):
    """Schema cho response product."""
    id: str = Field(..., description="Product ID (MongoDB ObjectId)")
    name: str
    description: str
    price: float
    category: str
    is_active: bool
    tenant_id: str
