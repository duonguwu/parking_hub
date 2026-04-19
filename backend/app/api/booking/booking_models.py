# -*- coding: utf-8 -*-
"""Booking Model — Customer reservations + full state machine."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


# State machine — see phase2_matching_engine.md §3.1
BOOKING_STATUSES = [
    "pending",              # just created, waiting garage confirm
    "confirmed",            # garage accepted
    "customer_arriving",    # user tapped "departing"
    "customer_arrived",     # check-in (QR or GPS)
    "in_service",           # staff started service
    "completed",            # done
    "cancelled_by_customer",
    "cancelled_by_garage",
    "no_show",
    "expired",              # pending too long
    "interrupted",          # equipment failure etc
]

# Valid transitions  current -> {allowed next states}
BOOKING_TRANSITIONS = {
    "pending": {"confirmed", "cancelled_by_customer", "cancelled_by_garage", "expired"},
    "confirmed": {"customer_arriving", "cancelled_by_customer", "cancelled_by_garage", "no_show"},
    "customer_arriving": {"customer_arrived", "no_show", "cancelled_by_customer"},
    "customer_arrived": {"in_service", "cancelled_by_garage"},
    "in_service": {"completed", "interrupted"},
    # Terminal
    "completed": set(),
    "cancelled_by_customer": set(),
    "cancelled_by_garage": set(),
    "no_show": set(),
    "expired": set(),
    "interrupted": set(),
}


def is_terminal(status: str) -> bool:
    return len(BOOKING_TRANSITIONS.get(status, set())) == 0


def can_transition(from_status: str, to_status: str) -> bool:
    return to_status in BOOKING_TRANSITIONS.get(from_status, set())


@mongo_instance.register
class BookingModel(TenantAwareDocument):
    booking_code = fields.StringField(required=True)   # human-readable WM-YYYYMMDD-NNNN

    # Parties
    customer_id = fields.ObjectIdField(required=True)
    garage_id = fields.ObjectIdField(required=True)
    vehicle_id = fields.ObjectIdField(allow_none=True, default=None)

    # Service
    service_type_code = fields.StringField(required=True)
    price = fields.IntegerField(default=0)                # VND at booking time

    # Timing
    requested_time = fields.AwareDateTimeField(required=True)
    estimated_arrival = fields.AwareDateTimeField(allow_none=True, default=None)

    # Status
    status = fields.StringField(default="pending")

    # Full timestamp trail — data moat
    timestamps = fields.DictField(default=dict)
    # { created_at, confirmed_at, customer_departed_at, customer_arrived_at,
    #   service_started_at, service_completed_at, cancelled_at }

    # Matching context snapshot
    matching_context = fields.DictField(default=dict)

    # Feedback
    feedback = fields.DictField(default=dict)
    # { rating (1-5), quick_feedback ("thumbs_up"/"thumbs_down"), comment }

    cancellation_reason = fields.StringField(default="")
    cancelled_by = fields.StringField(default="")     # "customer" | "garage" | "system"

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "bookings"
