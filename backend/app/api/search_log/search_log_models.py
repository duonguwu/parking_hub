# -*- coding: utf-8 -*-
"""Search Logs — data moat from day 1 (every match request + decision)."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class SearchLogModel(TenantAwareDocument):
    # tenant_id always "platform"
    customer_id = fields.ObjectIdField(allow_none=True, default=None)    # nullable (anonymous)
    session_id = fields.StringField(default="")

    # Search input (flattened)
    search_location = fields.DictField(default=dict)       # GeoJSON Point
    vehicle_type = fields.StringField(default="")
    service_type_code = fields.StringField(default="")
    requested_time = fields.AwareDateTimeField(allow_none=True, default=None)

    # Context snapshot
    context = fields.DictField(default=dict)
    # { hour_of_day, day_of_week, is_peak_hour, weather, district, traffic_multiplier, area_demand }

    # Results
    results_count = fields.IntegerField(default=0)
    results_shown = fields.ListField(fields.DictField(), default=list)
    # each: { garage_id (str), rank, match_score, component_scores, travel_min, predicted_wait }

    weights_used = fields.DictField(default=dict)          # context weights applied

    # User action (filled async after user interacts)
    action = fields.StringField(default="shown")           # shown | booked | viewed_details | abandoned
    selected_garage_id = fields.StringField(default="")
    selected_rank = fields.IntegerField(default=0)
    time_spent_seconds = fields.IntegerField(default=0)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "search_logs"
