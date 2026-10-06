# -*- coding: utf-8 -*-
"""Capacity Snapshots — chuỗi thời gian lấp đầy theo giờ của từng bãi."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class CapacitySnapshotModel(TenantAwareDocument):
    garage_id = fields.ObjectIdField(required=True)
    timestamp = fields.AwareDateTimeField(required=True)   # đầu giờ (UTC)

    total_spots = fields.IntegerField(default=0)
    occupied = fields.IntegerField(default=0)              # xe đang trong bãi
    held = fields.IntegerField(default=0)                  # chỗ đang giữ cho lượt đặt
    available = fields.IntegerField(default=0)
    occupancy_rate = fields.FloatField(default=0.0)        # (occupied + held) / total
    source = fields.StringField(default="manual")          # manual | simulated | checkin

    # Khoá tổng hợp theo giờ địa phương (Asia/Ho_Chi_Minh)
    hour_of_day = fields.IntegerField(default=0)           # 0-23
    day_of_week = fields.IntegerField(default=0)           # 0=T2, 6=CN

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "capacity_snapshots"
