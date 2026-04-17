# -*- coding: utf-8 -*-
"""MongoDB ObjectId Converter — Safe conversion."""
from typing import Union
from bson import ObjectId


def convert_mongo_object_id(obj_id: Union[ObjectId, str]):
    if isinstance(obj_id, ObjectId):
        return obj_id
    if isinstance(obj_id, str):
        try:
            return ObjectId(obj_id)
        except Exception as e:
            print(f"Invalid ObjectId string: {obj_id}, error: {e}")
            return False
