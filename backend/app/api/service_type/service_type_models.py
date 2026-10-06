# -*- coding: utf-8 -*-
"""Service Type — Danh mục dịch vụ cấp nền tảng (gửi xe, gói, dịch vụ kèm)."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


# parking: gửi lượt (giờ/đêm/ngày) — subscription: gói định kỳ — addon: dịch vụ kèm
SERVICE_CATEGORIES = ["parking", "subscription", "addon"]
# Đơn vị hiển thị giá
SERVICE_UNITS = ["hour", "night", "day", "workday", "month", "session"]


@mongo_instance.register
class ServiceTypeModel(TenantAwareDocument):
    # tenant_id always "platform" for this collection
    code = fields.StringField(required=True)         # unique, ví dụ "park_hourly"
    name = fields.StringField(required=True)
    category = fields.StringField(default="parking")
    unit = fields.StringField(default="hour")
    icon = fields.StringField(default="clock")        # tên icon lucide
    description = fields.StringField(default="")

    base_price_min = fields.IntegerField(default=0)   # VND — khoảng giá tham khảo thị trường
    base_price_max = fields.IntegerField(default=0)
    estimated_duration_minutes = fields.IntegerField(default=60)
    default_pricing = fields.DictField(default=dict)  # mẫu bảng giá khi chủ bãi thêm dịch vụ

    is_popular = fields.BooleanField(default=False)
    sort_order = fields.IntegerField(default=100)
    is_active = fields.BooleanField(default=True)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "service_types"
