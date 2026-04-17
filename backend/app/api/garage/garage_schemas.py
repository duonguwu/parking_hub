# -*- coding: utf-8 -*-
"""Garage API Schemas — Request/Response models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GarageCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address_street: str = Field(..., min_length=1)
    address_ward: str = Field(default="")
    address_district: str = Field(..., min_length=1)
    address_city: str = Field(..., min_length=1)
    address_province: str = Field(default="")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    total_bays: int = Field(default=2, ge=1, le=50)
    description: str = Field(default="")
    services_offered: List[str] = Field(default=[])
    vehicle_types_accepted: List[str] = Field(default=["standard"])
    amenities: List[str] = Field(default=[])


class GarageUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    services_offered: Optional[List[str]] = None
    vehicle_types_accepted: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    is_accepting_bookings: Optional[bool] = None
    operating_hours: Optional[Dict[str, Any]] = None


class GarageCapacityUpdateRequest(BaseModel):
    vehicles_in_service: int = Field(..., ge=0)
    vehicles_waiting: int = Field(..., ge=0)
    estimated_wait_minutes: int = Field(default=0, ge=0)


class GarageSearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    max_distance_km: float = Field(default=10, ge=1, le=50)
    min_tier: int = Field(default=1, ge=1, le=4)
    service_type: Optional[str] = None
    status: str = Field(default="active")
