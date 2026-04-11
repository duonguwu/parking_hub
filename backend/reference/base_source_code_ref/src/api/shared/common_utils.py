# -*- coding: utf-8 -*-
"""
Common Utils — Shared utility functions across all API modules.

Usage:
    from app.api.shared.common_utils import api_response, validate_id_format
    from app.api.shared.schemas import Operation, Resource
"""
import re
from typing import Optional, Dict, Any, Union
from app.api.shared.schemas import Operation, Resource


def validate_id_format(id_value: str, pattern: Optional[str] = None) -> bool:
    """
    Validate ID format.

    Args:
        id_value: ID value to validate
        pattern:  Optional regex pattern, default is alphanumeric + underscore + hyphen

    Returns:
        bool: True if valid
    """
    if not id_value or not isinstance(id_value, str):
        return False

    if len(id_value.strip()) == 0:
        return False

    # Default pattern: alphanumeric + underscore + hyphen
    if pattern is None:
        pattern = r'^[a-zA-Z0-9_-]+$'

    return bool(re.match(pattern, id_value))


def api_response(
    operation: Union[Operation, str],
    resource: Union[Resource, str, None] = None,
    data: Optional[Any] = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create standardized API response.

    Args:
        operation: Operation type (enum or string)
        resource:  Resource name (enum or string, optional)
        data:      Response data (optional)
        message:   Custom message (optional, auto-generated if not provided)

    Returns:
        dict: {"status": "ok", "message": "...", "data": ...}

    Examples:
        api_response(Operation.RETRIEVED, Resource.ITEMS, items_data)
        api_response(Operation.CREATED, Resource.ITEM, {"id": "123"})
        api_response(Operation.DELETED, Resource.ITEM)
        api_response("custom", message="Operation completed")
    """
    op_str = operation.value if isinstance(operation, Operation) else operation
    resource_str = resource.value if isinstance(resource, Resource) else resource

    if message is None:
        if resource_str:
            message = f"{resource_str.title()} {op_str} successfully"
        else:
            message = f"Operation {op_str} successfully"

    response = {
        "status": "ok",
        "message": message,
    }

    if data is not None:
        response["data"] = data

    return response
