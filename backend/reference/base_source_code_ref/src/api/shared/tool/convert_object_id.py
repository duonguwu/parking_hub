# -*- coding: utf-8 -*-
"""
MongoDB ObjectId Converter — Safe conversion tu string sang ObjectId.

Usage:
    from app.api.shared.tool.convert_object_id import convert_mongo_object_id

    oid = convert_mongo_object_id("507f1f77bcf86cd799439011")
    # -> ObjectId("507f1f77bcf86cd799439011")

    oid = convert_mongo_object_id("invalid")
    # -> False
"""
from typing import Union

from bson import ObjectId


def convert_mongo_object_id(obj_id: Union[ObjectId, str]):
    """
    Convert string to MongoDB ObjectId.

    Args:
        obj_id: ObjectId instance or string representation

    Returns:
        ObjectId if valid, False if invalid string
    """
    if isinstance(obj_id, ObjectId):
        return obj_id
    if isinstance(obj_id, str):
        try:
            return ObjectId(obj_id)
        except Exception as e:
            print(f"Invalid ObjectId string: {obj_id}, error: {e}")
            return False
