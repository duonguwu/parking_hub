# -*- coding: utf-8 -*-
"""User Model — MongoDB document for all user types."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class UserModel(TenantAwareDocument):
    username = fields.StringField(required=True)
    email = fields.StringField(required=True)
    phone = fields.StringField(default="")
    password_hash = fields.StringField(required=True)
    name = fields.StringField(default="")

    role = fields.StringField(default="customer")
    # "super_admin" | "platform_ops" | "garage_owner" | "garage_manager"
    # "garage_staff" | "customer" | "fleet_manager"

    is_active = fields.BooleanField(default=True)

    # Customer-specific profile
    customer_profile = fields.DictField(default=dict)
    # { vetc_id, default_vehicle_id, preferred_tier, home_location, work_location }

    # Staff-specific profile
    staff_profile = fields.DictField(default=dict)
    # { position, shift }

    # For center/chain managers managing multiple tenants
    # Stored as list of strings, but using DictField to allow None
    allowed_tenant_ids = fields.ListField(fields.StringField(), default=list)

    last_login = fields.AwareDateTimeField(allow_none=True, default=None)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "users"
