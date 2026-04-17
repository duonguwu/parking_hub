# -*- coding: utf-8 -*-
"""Tenant Model — MongoDB document for tenant/organization registry."""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class TenantModel(TenantAwareDocument):
    name = fields.StringField(required=True)
    slug = fields.StringField(required=True)
    type = fields.StringField(default="garage")  # "garage" | "chain" | "platform"
    status = fields.StringField(default="active")  # "pending" | "active" | "suspended"
    owner_user_id = fields.StringField(default="")

    contact = fields.DictField(default=dict)
    # { phone, email, address }

    subscription_plan = fields.StringField(default="free")
    # "free" | "basic" | "pro" | "enterprise"

    settings = fields.DictField(default=lambda: {
        "timezone": "Asia/Ho_Chi_Minh",
        "currency": "VND",
        "language": "vi",
    })

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "tenants"
