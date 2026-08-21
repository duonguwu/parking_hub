# -*- coding: utf-8 -*-
"""Service Type — Danh mục dịch vụ cấp nền tảng (đang là dữ liệu mẫu)."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


# Categories of service
# Dữ liệu mẫu, chốt lại khi thiết kế nghiệp vụ đỗ xe.
SERVICE_CATEGORIES = ["hourly", "overnight", "daily", "monthly", "other"]


@mongo_instance.register
class ServiceTypeModel(TenantAwareDocument):
    # tenant_id always "platform" for this collection
    code = fields.StringField(required=True)         # unique, ví dụ "park_hourly"
    name = fields.StringField(required=True)
    category = fields.StringField(default="hourly")
    description = fields.StringField(default="")

    base_price_min = fields.IntegerField(default=0)   # VND
    base_price_max = fields.IntegerField(default=0)
    estimated_duration_minutes = fields.IntegerField(default=30)

    minimum_tier = fields.IntegerField(default=1)     # 1-4
    # Multiplier by vehicle type (price scaling)
    vehicle_type_multiplier = fields.DictField(default=dict)
    # {"standard": 1.0, "premium": 1.3, "luxury": 1.6, "super": 2.0}

    is_active = fields.BooleanField(default=True)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "service_types"
