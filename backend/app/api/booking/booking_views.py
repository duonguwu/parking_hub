# -*- coding: utf-8 -*-
"""Booking Views — giữ chỗ, vào/ra bãi, huỷ, đánh giá."""
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from app.api.booking.booking_utils import (
    create_booking, confirm_booking, reject_booking, checkin_booking, checkout_booking,
    mark_no_show, mark_paid, cancel_booking, submit_feedback, list_bookings_for_user, get_booking,
)
from app.api.auth.dependencies import get_current_user
from app.api.auth.permissions import require_permission
from app.api.shared.common_utils import api_response
from app.api.shared.schemas import Operation, Resource

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])


class CreateBookingInput(BaseModel):
    garage_id: str = Field(..., min_length=1)
    service_type_code: str = Field(..., min_length=1)
    start_time: datetime
    end_time: Optional[datetime] = None
    vehicle_id: Optional[str] = None
    license_plate: Optional[str] = Field(None, max_length=20)
    matching_context: Optional[Dict[str, Any]] = None


class BookingIdInput(BaseModel):
    id: str = Field(..., min_length=1)


class ReasonInput(BaseModel):
    id: str = Field(..., min_length=1)
    reason: str = Field(default="", max_length=300)


class CheckinInput(BaseModel):
    id: str = Field(..., min_length=1)
    license_plate: Optional[str] = Field(None, max_length=20)


class CheckoutInput(BaseModel):
    id: str = Field(..., min_length=1)
    payment_method: Optional[str] = Field(None, pattern="^(cash|transfer)$")


class PaymentInput(BaseModel):
    id: str = Field(..., min_length=1)
    payment_method: str = Field(..., pattern="^(cash|transfer)$")


class FeedbackInput(BaseModel):
    id: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)
    quick_feedback: Optional[str] = Field(None, pattern="^(thumbs_up|thumbs_down)$")
    comment: Optional[str] = Field(None, max_length=1000)
    complaint: Optional[bool] = None


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
        start_time=input_data.start_time,
        end_time=input_data.end_time,
        vehicle_id=input_data.vehicle_id,
        license_plate=input_data.license_plate,
        matching_context=input_data.matching_context,
        source="matching" if input_data.matching_context else "app",
    )
    return api_response(Operation.CREATED, Resource.BOOKING, data)


@booking_router.post("/feedback")
async def feedback(
    input_data: FeedbackInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await submit_feedback(
        input_data.id, current_user,
        rating=input_data.rating, quick_feedback=input_data.quick_feedback,
        comment=input_data.comment, complaint=input_data.complaint,
    )
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


# ── Garage staff actions ────────────────────────────────────────

@booking_router.post("/confirm")
async def confirm(
    input_data: BookingIdInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    return api_response(Operation.UPDATED, Resource.BOOKING, await confirm_booking(input_data.id, current_user))


@booking_router.post("/reject")
async def reject(
    input_data: ReasonInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await reject_booking(input_data.id, current_user, input_data.reason)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/checkin")
async def checkin(
    input_data: CheckinInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await checkin_booking(input_data.id, current_user, input_data.license_plate)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/checkout")
async def checkout(
    input_data: CheckoutInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await checkout_booking(input_data.id, current_user, input_data.payment_method)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


@booking_router.post("/no_show")
async def no_show(
    input_data: BookingIdInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    return api_response(Operation.UPDATED, Resource.BOOKING, await mark_no_show(input_data.id, current_user))


@booking_router.post("/mark_paid")
async def paid(
    input_data: PaymentInput,
    current_user: dict = Depends(require_permission(["booking:edit"])),
) -> Dict[str, Any]:
    data = await mark_paid(input_data.id, current_user, input_data.payment_method)
    return api_response(Operation.UPDATED, Resource.BOOKING, data)


# ── Shared (customer OR garage) ─────────────────────────────────

@booking_router.post("/cancel")
async def cancel(
    input_data: ReasonInput,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    data = await cancel_booking(input_data.id, current_user, input_data.reason)
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
