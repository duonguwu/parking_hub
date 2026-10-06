# -*- coding: utf-8 -*-
"""Garage Service — Per-garage service offerings (price + duration override)."""
from umongo import fields
from bson import ObjectId
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class GarageServiceModel(TenantAwareDocument):
    garage_id = fields.ObjectIdField(required=True)
    service_type_code = fields.StringField(required=True)

    # Garage-specific overrides
    price = fields.IntegerField(required=True)              # VND — giá hiển thị (block đầu / trọn gói)
    estimated_duration_minutes = fields.IntegerField(default=30)
    pricing = fields.DictField(default=dict)                # xem garage_service/pricing_utils.py
    note = fields.StringField(default="")                   # ghi chú cho khách, ví dụ "18:00–07:00"

    is_available = fields.BooleanField(default=True)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "garage_services"
