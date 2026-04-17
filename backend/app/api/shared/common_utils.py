# -*- coding: utf-8 -*-
"""
Common Utils — Shared utility functions across all API modules.

Usage:
    from app.api.shared.common_utils import api_response, validate_id_format
"""
import re
from typing import Optional, Dict, Any, Union
from app.api.shared.schemas import Operation, Resource


def validate_id_format(id_value: str, pattern: Optional[str] = None) -> bool:
    if not id_value or not isinstance(id_value, str):
        return False
    if len(id_value.strip()) == 0:
        return False
    if pattern is None:
        pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, id_value))


def api_response(
    operation: Union[Operation, str],
    resource: Union[Resource, str, None] = None,
    data: Optional[Any] = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    op_str = operation.value if isinstance(operation, Operation) else operation
    resource_str = resource.value if isinstance(resource, Resource) else resource

    if message is None:
        if resource_str:
            message = f"{resource_str.title()} {op_str} successfully"
        else:
            message = f"Operation {op_str} successfully"

    response = {"status": "ok", "message": message}
    if data is not None:
        response["data"] = data
    return response
