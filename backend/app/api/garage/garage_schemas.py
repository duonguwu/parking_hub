# -*- coding: utf-8 -*-
"""Garage API Schemas — Request/Response models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CapacityInput(BaseModel):
    total_spots: Optional[int] = Field(None, ge=1, le=5000)
    walk_in_spots: Optional[int] = Field(None, ge=0, le=5000)
    monthly_spots: Optional[int] = Field(None, ge=0, le=5000)
    reservable_ratio: Optional[float] = Field(None, ge=0, le=1)
    grace_minutes: Optional[int] = Field(None, ge=0, le=180)


class LatLngInput(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class GarageProfileUpdate(BaseModel):
    """Chủ bãi sửa hồ sơ. Cấp tích hợp / hạng sao / trạng thái do admin đặt."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    lot_type: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    contacts: Optional[Dict[str, str]] = None
    operating_hours: Optional[Dict[str, Any]] = None
    is_accepting_bookings: Optional[bool] = None
    photos: Optional[List[str]] = None
    capacity: Optional[CapacityInput] = None
    attributes: Optional[Dict[str, Any]] = None
    entrance: Optional[LatLngInput] = None


class GarageSearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_distance_km: float = Field(default=5, ge=0.2, le=50)
    lot_types: Optional[List[str]] = None
    covered: bool = False
    ev: bool = False
    min_height_m: Optional[float] = Field(None, ge=1.5, le=5)
    guard_24h: bool = False
    no_flood: bool = False
    min_grade: int = Field(default=1, ge=1, le=5)
    max_hourly_price: Optional[int] = Field(None, ge=0)
    service_type: Optional[str] = None
    only_available: bool = False
