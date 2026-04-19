# -*- coding: utf-8 -*-
"""Booking Views — full state machine endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from app.api.booking.booking_utils import (
    create_booking, confirm_booking, depart_booking, checkin_booking,
    start_service, complete_service, cancel_booking,
    submit_feedback, list_bookings_for_user, get_booking,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])


class CreateBookingInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    service_type_code: str = Field(..., min_length=1)
    requested_time: datetime
    vehicle_id: Optional[str] = None
    matching_context: Optional[Dict[str, Any]] = None


class BookingIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class CheckinInput(BaseModel):
    id: str = Field(..., min_length=1)
    method: str = Field(default="gps", pattern="^(gps|qr)$")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)


class CancelInput(BaseModel):
    id: str = Field(..., min_length=1)
    reason: str = ""
    cancelled_by: str = Field(default="customer", pattern="^(customer|garage)$")


class FeedbackInput(BaseModel):
    id: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    quick_feedback: Optional[str] = Field(None, pattern="^(thumbs_up|thumbs_down)$")
    comment: Optional[str] = Field(None, max_length=1000)


class ListFilterInput(BaseModel):
    status: Optional[str] = None


# ── Customer actions ────────────────────────────────────────────

@booking_router.post("/create")
async def create(
    input_data: CreateBookingInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await create_booking(
        customer_id=current_user["user_id"],
        garage_id=input_data.garage_id,
        service_type_code=input_data.service_type_code,
        requested_time=input_data.requested_time,
        vehicle_id=input_data.vehicle_id,
        matching_context=input_data.matching_context,
    )
    return api_response(Operation.CREATED, Resource.BOOKING, data)


@booking_router.post("/depart")
async def depart(
    input_data: BookingIdInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await depart_booking(input_data.id, current_user)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/checkin")
async def checkin(
    input_data: CheckinInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await checkin_booking(
        input_data.id, current_user,
        method=input_data.method, lat=input_data.lat, lng=input_data.lng,
    )
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/feedback")
async def feedback(
    input_data: FeedbackInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await submit_feedback(
        input_data.id, current_user,
        rating=input_data.rating,
        quick_feedback=input_data.quick_feedback,
        comment=input_data.comment,
    )
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


# ── Garage staff actions ────────────────────────────────────────

@booking_router.post("/confirm")
async def confirm(
    input_data: BookingIdInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await confirm_booking(input_data.id, current_user)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/start_service")
async def start(
    input_data: BookingIdInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await start_service(input_data.id, current_user)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/complete")
async def complete(
    input_data: BookingIdInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await complete_service(input_data.id, current_user)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


# ── Shared (customer OR garage) ─────────────────────────────────

@booking_router.post("/cancel")
async def cancel(
    input_data: CancelInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    # Enforce: customer can only cancel as "customer"; garage staff as "garage"
    role = current_user.get("role", "")
    by = input_data.cancelled_by
    if role == "customer" and by != "customer":
        by = "customer"
    data = await cancel_booking(input_data.id, current_user, input_data.reason, by)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/get_all")
async def list_bookings(
    input_data: ListFilterInput = ListFilterInput(),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await list_bookings_for_user(current_user, input_data.status)
    return api_response(Operation.RETRIEVED, Resource.BOOKINGS, data)


@booking_router.post("/get_by_id")
async def get_by_id(
    input_data: BookingIdInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await get_booking(input_data.id, current_user)
    return api_response(Operation.RETRIEVED, Resource.BOOKING, data)
