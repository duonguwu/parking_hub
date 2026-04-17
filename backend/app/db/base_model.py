# -*- coding: utf-8 -*-
"""
TenantAwareDocument — Base model with automatic multi-tenant isolation.

Moi model ke thua class nay se tu dong:
- Yeu cau current_user khi find/find_one
- Filter theo tenant_id cua current_user
- Super admin (tenant_id == "super_admin") thay tat ca
- Center manager (co allowed_tenant_ids) thay nhieu tenant con

Usage:
    @mongo_instance.register
    class GarageModel(TenantAwareDocument):
        name = fields.StringField(required=True)

        class Meta(TenantAwareDocument.Meta):
            abstract = False
            collection_name = "garages"

    # Query — tenant filter tu dong
    garages = await GarageModel.find({}, current_user=current_user)
"""
from typing import Optional

from fastapi import HTTPException, status
from umongo import Document, fields

from app.api.shared.tool.datetime_convert import get_current_time
from app.api.shared.tool.convert_object_id import convert_mongo_object_id
from app.db.mongo import mongo_instance


@mongo_instance.register
class TenantAwareDocument(Document):
    """
    Base model with automatic tenant isolation.

    Fields:
        tenant_id  : required, auto-injected into every query
        created_at : auto-set on create
        created_by : username, default "system"
        updated_at : auto-set on create/update
        updated_by : username, default "system"
    """
    created_at = fields.AwareDateTimeField(default=get_current_time)
    created_by = fields.StringField(default="system")
    updated_at = fields.AwareDateTimeField(default=get_current_time)
    updated_by = fields.StringField(default="system")
    tenant_id = fields.StringField(required=True)

    class Meta:
        abstract = True
        strict = False

    # ─── Internal helpers ────────────────────────────────────────

    @classmethod
    def _require_user(cls, current_user: Optional[dict]):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="current_user is required for this operation",
            )
        return current_user

    @classmethod
    def _add_tenant_filter(cls, filter_dict: Optional[dict], current_user: dict) -> dict:
        current_user = cls._require_user(current_user)
        filter_dict = filter_dict or {}

        if current_user.get("tenant_id") != "super_admin":
            allowed_tenants = current_user.get("allowed_tenant_ids")
            if allowed_tenants:  # non-empty list only ([] is falsy → fall through to single tenant)
                filter_dict["tenant_id"] = {"$in": allowed_tenants}
            else:
                filter_dict["tenant_id"] = current_user.get("tenant_id")

        return filter_dict

    @classmethod
    def _extract_filter_and_user(cls, *args, **kwargs):
        current_user = kwargs.pop("current_user", None)
        current_user = cls._require_user(current_user)

        if args:
            filter_arg, args = args[0], args[1:]
        else:
            filter_arg = kwargs.pop("filter", None)

        if filter_arg is None:
            filter_arg = {}

        return filter_arg, current_user, args, kwargs

    # ─── Override find / find_one ────────────────────────────────

    @classmethod
    def find(cls, *args, **kwargs):
        filter_arg, current_user, args, kwargs = cls._extract_filter_and_user(*args, **kwargs)
        filtered = cls._add_tenant_filter(filter_arg, current_user)
        return super(TenantAwareDocument, cls).find(filtered, *args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        filter_arg, current_user, args, kwargs = cls._extract_filter_and_user(*args, **kwargs)
        filtered = cls._add_tenant_filter(filter_arg, current_user)
        return super(TenantAwareDocument, cls).find_one(filtered, *args, **kwargs)

    # ─── Tenant target resolution ────────────────────────────────

    @classmethod
    def _determine_target_tenant(cls, current_user: dict, target_tenant_id: Optional[str] = None) -> str:
        current_user = cls._require_user(current_user)
        if current_user.get("tenant_id") == "super_admin":
            return target_tenant_id or current_user.get("tenant_id")

        allowed_tenants = current_user.get("allowed_tenant_ids")
        if target_tenant_id and allowed_tenants and target_tenant_id in allowed_tenants:
            return target_tenant_id

        return current_user.get("tenant_id")

    # ─── Check name unique ───────────────────────────────────────

    @classmethod
    async def check_name_exists_in_tenant(
        cls,
        name_field: str,
        name_value: str,
        current_user: dict,
        target_tenant_id: Optional[str] = None,
        exclude_id: Optional[str] = None,
    ) -> bool:
        effective_tenant_id = cls._determine_target_tenant(current_user, target_tenant_id)
        filter_dict = {
            name_field: name_value,
            "tenant_id": effective_tenant_id,
        }

        if exclude_id:
            filter_dict["_id"] = {"$ne": convert_mongo_object_id(exclude_id)}

        result = await cls.collection.find_one(filter_dict)
        return result is not None

    # ─── CRUD helpers ────────────────────────────────────────────

    @classmethod
    async def create_with_tenant_check(
        cls,
        data_dict: dict,
        current_user: dict,
        name_field: str = "name",
        target_tenant_id: Optional[str] = None,
        **extra_fields,
    ):
        effective_tenant_id = cls._determine_target_tenant(current_user, target_tenant_id)

        if name_field in data_dict:
            name_exists = await cls.check_name_exists_in_tenant(
                name_field=name_field,
                name_value=data_dict[name_field],
                current_user=current_user,
                target_tenant_id=target_tenant_id,
            )
            if name_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"{name_field} already exists in this tenant",
                )

        doc_data = {
            **data_dict,
            **extra_fields,
            "tenant_id": effective_tenant_id,
            "created_at": get_current_time(),
            "created_by": current_user.get("username", "system"),
            "updated_at": get_current_time(),
            "updated_by": current_user.get("username", "system"),
        }

        try:
            doc = cls(**doc_data)
            await doc.commit()
            return doc
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @classmethod
    async def update_with_tenant_check(
        cls,
        doc_id: str,
        update_data: dict,
        current_user: dict,
        name_field: str = "name",
        target_tenant_id: Optional[str] = None,
    ):
        oid = convert_mongo_object_id(doc_id)

        doc = await cls.find_one({"_id": oid}, current_user=current_user)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if name_field in update_data:
            name_exists = await cls.check_name_exists_in_tenant(
                name_field=name_field,
                name_value=update_data[name_field],
                current_user=current_user,
                target_tenant_id=target_tenant_id,
                exclude_id=doc_id,
            )
            if name_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"{name_field} already exists in this tenant",
                )

        set_data = {
            **update_data,
            "updated_at": get_current_time(),
            "updated_by": current_user.get("username", "system"),
        }

        result = await cls.collection.update_one({"_id": oid}, {"$set": set_data})
        return result.modified_count > 0

    @classmethod
    async def delete_with_tenant_check(
        cls,
        doc_id: str,
        current_user: dict,
        target_tenant_id: Optional[str] = None,
        check_usage_callback: Optional[callable] = None,
    ):
        oid = convert_mongo_object_id(doc_id)

        doc = await cls.find_one({"_id": oid}, current_user=current_user)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if check_usage_callback:
            await check_usage_callback(doc, current_user)

        effective_tenant_id = cls._determine_target_tenant(current_user, target_tenant_id)
        result = await cls.collection.delete_one(
            {"_id": oid, "tenant_id": effective_tenant_id}
        )

        return result.deleted_count > 0

    @classmethod
    async def get_by_id_with_tenant_check(
        cls,
        doc_id: str,
        current_user: dict,
        projection: Optional[dict] = None,
    ):
        oid = convert_mongo_object_id(doc_id)
        return await cls.find_one(
            {"_id": oid},
            current_user=current_user,
            projection=projection,
        )
