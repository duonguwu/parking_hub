# -*- coding: utf-8 -*-
"""Vehicle API Schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class VehicleCreateRequest(BaseModel):
    license_plate: str = Field(..., min_length=1, max_length=20)
    brand: str = Field(default="", max_length=50)
    model: str = Field(default="", max_length=50)
    year: int = Field(default=2024, ge=1990, le=2030)
    color: str = Field(default="", max_length=30)
    vehicle_type: str = Field(default="standard")  # standard | premium | luxury | super
    body_type: str = Field(default="sedan")  # sedan | suv | hatchback | truck | van | coupe
    size_class: str = Field(default="medium")  # compact | medium | large | xl
    is_default: bool = Field(default=False)


class VehicleUpdateRequest(BaseModel):
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None, ge=1990, le=2030)
    color: Optional[str] = Field(None, max_length=30)
    vehicle_type: Optional[str] = None
    body_type: Optional[str] = None
    size_class: Optional[str] = None
    is_default: Optional[bool] = None
