# -*- coding: utf-8 -*-
"""
Garage Model — hồ sơ bãi đỗ xe (giữ tên `garage` trong code, nghiệp vụ là parking lot).

4 trục phân loại (xem garage_classification_utils.py):
  - lot_type           loại hình bãi (tầng hầm chung cư, nhà xe chuyên dụng, ...)
  - integration_level  cấp tích hợp dữ liệu 1–4, admin đặt
  - grade              hạng sao 1–5 từ checklist kiểm định 100 điểm, admin đặt
  - quality_score      0–100, tính từ vận hành thực tế (giữ chỗ, khiếu nại, quay lại)
"""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


def _default_hours():
    return {
        "is_24h": False,
        "monday":    {"open": "06:00", "close": "22:00"},
        "tuesday":   {"open": "06:00", "close": "22:00"},
        "wednesday": {"open": "06:00", "close": "22:00"},
        "thursday":  {"open": "06:00", "close": "22:00"},
        "friday":    {"open": "06:00", "close": "22:00"},
        "saturday":  {"open": "06:00", "close": "22:00"},
        "sunday":    {"open": "06:00", "close": "22:00"},
    }


@mongo_instance.register
class GarageModel(TenantAwareDocument):
    name = fields.StringField(required=True)
    slug = fields.StringField(required=True)

    # ── Location (GeoJSON Point) ──
    location = fields.DictField(required=True)
    # { "type": "Point", "coordinates": [lng, lat] }
    entrance_location = fields.DictField(default=dict)   # cổng vào xe, có thể khác tâm bãi
    address = fields.DictField(default=dict)
    # { street, ward, district, city, province }

    # ── Phân loại ──
    lot_type = fields.StringField(default="outdoor_commercial")
    integration_level = fields.IntegerField(default=1)    # 1..4
    grade = fields.IntegerField(default=1)                # 1..5 sao
    grade_score = fields.IntegerField(default=0)          # 0..100 từ checklist
    grade_assessment = fields.DictField(default=dict)
    # { items: {key: bool}, assessed_at, assessed_by, note }
    quality_score = fields.FloatField(default=0.0)        # 0..100 từ vận hành
    next_inspection_at = fields.AwareDateTimeField(allow_none=True, default=None)

    # ── Sức chứa ──
    capacity = fields.DictField(default=lambda: {
        "total_spots": 20,
        "walk_in_spots": 10,       # chỗ dành cho khách vãng lai
        "monthly_spots": 0,        # chỗ cho thuê tháng
        "reservable_ratio": 0.5,   # tỉ lệ tối đa được đặt trước
        "grace_minutes": 15,       # giữ chỗ sau giờ hẹn
    })

    # ── Thuộc tính vật lý ──
    attributes = fields.DictField(default=dict)
    # { cover: basement|full_roof|partial_roof|open, max_height_m, guard: none|hours|24h,
    #   guard_hours, cctv: none|partial|full, ev_chargers: {count, power_kw, connectors[]},
    #   flood_risk: none|heavy_rain|frequent, parking_style: self|attendant|stacked,
    #   vehicle_types: [sedan, suv, pickup, van, ...], large_vehicle_ok, lighting: good|basic|poor,
    #   surface: concrete|asphalt|gravel, fire_safety: bool, restroom: bool, payment_methods: [] }

    # ── Tình trạng chỗ trống (realtime) ──
    occupancy = fields.DictField(default=lambda: {
        "occupied": 0, "source": "manual", "updated_at": None,
    })

    operating_hours = fields.DictField(default=_default_hours)

    # ── Thông tin kinh doanh ──
    services_offered = fields.ListField(fields.StringField(), default=list)
    photos = fields.ListField(fields.StringField(), default=list)
    description = fields.StringField(default="")
    contacts = fields.DictField(default=dict)             # { phone, zalo, manager_name }

    # ── Trạng thái ──
    status = fields.StringField(default="pending_review")
    # "pending_review" | "active" | "suspended"
    is_verified = fields.BooleanField(default=False)
    is_accepting_bookings = fields.BooleanField(default=True)

    # ── Chỉ số vận hành (tính lại định kỳ) ──
    stats = fields.DictField(default=lambda: {
        "fulfillment_rate": 0.0,
        "no_show_rate": 0.0,
        "complaint_count": 0,
        "return_rate": 0.0,
        "avg_rating": 0.0,
        "rating_count": 0,
        "total_sessions": 0,
    })

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "garages"
