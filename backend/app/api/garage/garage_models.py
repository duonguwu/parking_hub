# -*- coding: utf-8 -*-
"""
Garage Model — MongoDB document for garage profiles.
Includes location (GeoJSON), tiering, capacity, and real-time load.
"""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class GarageModel(TenantAwareDocument):
    name = fields.StringField(required=True)
    slug = fields.StringField(required=True)

    # ── Location (GeoJSON Point) ──
    location = fields.DictField(required=True)
    # { "type": "Point", "coordinates": [lng, lat] }

    address = fields.DictField(default=dict)
    # { street, ward, district, city, province }

    # ── Tiering ──
    tier = fields.IntegerField(default=1)  # 1=Basic, 2=Standard, 3=Pro, 4=Elite
    tier_score = fields.FloatField(default=0.0)  # 0-100
    tier_assessment = fields.DictField(default=dict)
    # { equipment_score, process_score, staff_score, capacity_score, reliability_score,
    #   last_assessed_at, assessed_by }

    # ── Capacity ──
    capacity = fields.DictField(default=lambda: {
        "total_bays": 2,
        "max_vehicles_per_hour": 4,
        "avg_processing_time_minutes": 30,
    })

    operating_hours = fields.DictField(default=lambda: {
        "monday":    {"open": "07:00", "close": "20:00"},
        "tuesday":   {"open": "07:00", "close": "20:00"},
        "wednesday": {"open": "07:00", "close": "20:00"},
        "thursday":  {"open": "07:00", "close": "20:00"},
        "friday":    {"open": "07:00", "close": "21:00"},
        "saturday":  {"open": "07:00", "close": "21:00"},
        "sunday":    {"open": "08:00", "close": "18:00"},
    })

    # ── Business info ──
    services_offered = fields.ListField(fields.StringField(), default=list)
    vehicle_types_accepted = fields.ListField(fields.StringField(), default=lambda: ["standard"])
    amenities = fields.ListField(fields.StringField(), default=list)
    photos = fields.ListField(fields.StringField(), default=list)
    description = fields.StringField(default="")

    # ── Status ──
    status = fields.StringField(default="active")
    # "pending_review" | "active" | "suspended"
    is_verified = fields.BooleanField(default=False)
    is_accepting_bookings = fields.BooleanField(default=True)

    # ── Real-time load (updated frequently) ──
    current_load = fields.DictField(default=lambda: {
        "vehicles_in_service": 0,
        "vehicles_waiting": 0,
        "estimated_wait_minutes": 0,
        "last_updated": None,
    })

    # ── Aggregate stats (updated periodically) ──
    stats = fields.DictField(default=lambda: {
        "total_services": 0,
        "avg_rating": 0.0,
        "retention_rate": 0.0,
        "complaint_rate": 0.0,
        "avg_actual_processing_minutes": 0,
        "on_time_rate": 0.0,
    })

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "garages"
