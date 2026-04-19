# -*- coding: utf-8 -*-
"""Capacity Snapshots — Time-series tracking of garage load."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class CapacitySnapshotModel(TenantAwareDocument):
    garage_id = fields.ObjectIdField(required=True)
    timestamp = fields.AwareDateTimeField(required=True)

    vehicles_in_service = fields.IntegerField(default=0)
    vehicles_waiting = fields.IntegerField(default=0)
    available_bays = fields.IntegerField(default=0)
    estimated_wait_minutes = fields.IntegerField(default=0)
    staff_on_duty = fields.IntegerField(default=0)

    # Aggregated keys for baseline queries
    hour_of_day = fields.IntegerField(default=0)          # 0-23
    day_of_week = fields.IntegerField(default=0)          # 0=Mon, 6=Sun

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "capacity_snapshots"
