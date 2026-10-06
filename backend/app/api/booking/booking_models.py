# -*- coding: utf-8 -*-
"""Booking Model — lượt giữ chỗ / phiên gửi xe + state machine."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


# State machine, xem docs/04_technical/08_Codebase_Guide.md phần booking
BOOKING_STATUSES = [
    "pending",       # bãi cấp 2: chờ bãi xác nhận
    "reserved",      # đã giữ chỗ (cấp 3–4 tự xác nhận, cấp 2 sau khi bãi xác nhận)
    "checked_in",    # xe đã vào bãi
    "checked_out",   # xe đã ra, đã tính tiền
    "cancelled",     # khách huỷ, hoặc bãi huỷ sau khi đã giữ (cancelled_by)
    "rejected",      # bãi từ chối lượt pending
    "no_show",       # quá grace_until không đến
    "expired",       # pending quá giờ bắt đầu mà bãi chưa xác nhận
]

# Valid transitions  current -> {allowed next states}
BOOKING_TRANSITIONS = {
    "pending": {"reserved", "rejected", "cancelled", "expired"},
    "reserved": {"checked_in", "cancelled", "no_show"},
    "checked_in": {"checked_out"},
    # Terminal
    "checked_out": set(),
    "cancelled": set(),
    "rejected": set(),
    "no_show": set(),
    "expired": set(),
}

# Các trạng thái chiếm suất giữ chỗ trong khung giờ
HOLDING_STATUSES = ["pending", "reserved", "checked_in"]
ACTIVE_STATUSES = ["pending", "reserved", "checked_in"]


def is_terminal(status: str) -> bool:
    return len(BOOKING_TRANSITIONS.get(status, set())) == 0


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in BOOKING_TRANSITIONS.get(from_status, set())


@mongo_instance.register
class BookingModel(TenantAwareDocument):
    booking_code = fields.StringField(required=True)   # PH-YYYYMMDD-XXXX

    # Parties
    customer_id = fields.ObjectIdField(allow_none=True, default=None)   # None = khách vãng lai
    garage_id = fields.ObjectIdField(required=True)
    vehicle_id = fields.ObjectIdField(allow_none=True, default=None)
    license_plate = fields.StringField(default="")

    # Service
    service_type_code = fields.StringField(required=True)
    quoted_price = fields.IntegerField(default=0)      # VND, báo giá lúc đặt
    final_price = fields.IntegerField(allow_none=True, default=None)   # VND, tính lúc check-out
    payment_status = fields.StringField(default="unpaid")    # unpaid | paid
    payment_method = fields.StringField(default="")          # cash | transfer

    # Timing
    start_time = fields.AwareDateTimeField(required=True)
    end_time = fields.AwareDateTimeField(required=True)
    grace_until = fields.AwareDateTimeField(required=True)   # giữ chỗ tới lúc này

    # Status
    status = fields.StringField(default="pending")
    source = fields.StringField(default="app")               # app | walk_in | matching

    # Timestamp trail
    timestamps = fields.DictField(default=dict)
    # { created_at, reserved_at, checked_in_at, checked_out_at, cancelled_at, rejected_at,
    #   no_show_at, expired_at, paid_at }

    matching_context = fields.DictField(default=dict)
    feedback = fields.DictField(default=dict)
    # { rating (1-5), quick_feedback ("thumbs_up"/"thumbs_down"), comment, complaint: bool }

    cancellation_reason = fields.StringField(default="")
    cancelled_by = fields.StringField(default="")     # "customer" | "garage" | "system"

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "bookings"
