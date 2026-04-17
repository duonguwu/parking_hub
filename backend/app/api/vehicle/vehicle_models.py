# -*- coding: utf-8 -*-
"""Vehicle Model — MongoDB document for user vehicles."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


# ── Vehicle type → minimum garage tier mapping ──
VEHICLE_TIER_MAP = {
    "standard": 1,   # Xe phổ thông → Tier 1+
    "premium": 2,    # Xe cao cấp → Tier 2+
    "luxury": 3,     # Xe sang → Tier 3+
    "super": 4,      # Siêu xe → Tier 4 only
}

# ── Vehicle type → allowed tiers ──
VEHICLE_ALLOWED_TIERS = {
    "standard": [1, 2, 3, 4],
    "premium": [2, 3, 4],
    "luxury": [3, 4],
    "super": [4],
}


@mongo_instance.register
class VehicleModel(TenantAwareDocument):
    owner_user_id = fields.StringField(required=True)

    license_plate = fields.StringField(required=True)
    brand = fields.StringField(default="")
    model = fields.StringField(default="")
    year = fields.IntegerField(default=2024)
    color = fields.StringField(default="")

    # Classification
    vehicle_type = fields.StringField(default="standard")
    # "standard" | "premium" | "luxury" | "super"
    body_type = fields.StringField(default="sedan")
    # "sedan" | "suv" | "hatchback" | "truck" | "van" | "coupe"
    size_class = fields.StringField(default="medium")
    # "compact" | "medium" | "large" | "xl"

    minimum_garage_tier = fields.IntegerField(default=1)

    # VETC integration (future)
    vetc_vehicle_id = fields.StringField(default=None)
    vetc_linked = fields.BooleanField(default=False)

    is_default = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "vehicles"
