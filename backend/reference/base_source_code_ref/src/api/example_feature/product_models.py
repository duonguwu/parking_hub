# -*- coding: utf-8 -*-
"""
Product Models — MongoDB document model cho product feature.

Dung khi feature co collection MongoDB rieng.
Neu tai dung model tu module khac thi chi can import, khong tao file moi.

Usage:
    from app.api.example_feature.product_models import ProductModel

    # Query (tenant filter tu dong)
    products = await ProductModel.find({}, current_user=current_user)

    # Create
    doc = await ProductModel.create_with_tenant_check(
        data_dict={"name": "Product A", "price": 100, "category": "electronics"},
        current_user=current_user,
    )
"""
from umongo import fields
from app.db.mongo import mongo_instance
from app.db.base_model import TenantAwareDocument


@mongo_instance.register
class ProductModel(TenantAwareDocument):
    """
    Product document — example feature model.

    Inherits from TenantAwareDocument:
        - tenant_id (auto-filtered in queries)
        - created_at, created_by, updated_at, updated_by
    """
    name = fields.StringField(required=True)
    description = fields.StringField(default="")
    price = fields.FloatField(required=True)
    category = fields.StringField(default="general")
    is_active = fields.BooleanField(default=True)

    class Meta(TenantAwareDocument.Meta):
        abstract = False
        collection_name = "products"
        indexes = [
            ("tenant_id", "name"),      # Unique name per tenant
            ("tenant_id", "category"),   # Fast filter by category
        ]
