# -*- coding: utf-8 -*-
"""
DateTime Utilities — Timezone-aware datetime helpers.

Convention: Luu tru UTC trong DB, hien thi Asia/Bangkok (UTC+7) cho user.

Usage:
    from app.api.shared.tool.datetime_convert import (
        get_current_time,
        get_current_time_zone_7,
        get_current_timestamp,
        convert_to_hcm_or_bangkok_time,
    )
"""
import datetime
from typing import Optional

import pytz
from dateutil import parser


def get_current_time_zone_7(
    time_zone: str = "Asia/Bangkok",
) -> datetime.datetime:
    """Get current time in specified timezone (default Asia/Bangkok UTC+7)."""
    return datetime.datetime.now(pytz.timezone(time_zone))


def get_current_timestamp() -> int:
    """Get current UTC time as integer seconds since epoch."""
    current_time = datetime.datetime.now(pytz.timezone("Asia/Bangkok")).astimezone(pytz.utc)
    return int(round(current_time.timestamp()))


def get_current_time() -> datetime.datetime:
    """
    Get current time in UTC.
    Dung cho field default trong TenantAwareDocument.
    """
    current_time = datetime.datetime.now(pytz.timezone("Asia/Bangkok")).replace()
    return current_time.astimezone(pytz.utc)


def validate_time_format(
    time_str: str,
    format_time: str = "%Y-%m-%d %H:%M:%S",
) -> bool:
    """Validate time string matches expected format."""
    try:
        datetime.datetime.strptime(time_str, format_time)
        return True
    except Exception:
        return False


def convert_time_to_utc(time_str: str) -> datetime.datetime:
    """
    Convert time string (Asia/Bangkok) to UTC datetime.

    Args:
        time_str: Format "YYYY-MM-DD HH:MM:SS"

    Returns:
        UTC datetime object

    Raises:
        ValueError: If format invalid
    """
    if not validate_time_format(time_str):
        raise ValueError("Invalid time format. Expected format: YYYY-MM-DD HH:MM:SS")

    local_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    local_tz = pytz.timezone("Asia/Bangkok")
    local_dt = local_tz.localize(local_time)

    return local_dt.astimezone(pytz.utc)


def convert_to_hcm_or_bangkok_time(
    time_str: str | datetime.datetime,
    source_timezone: Optional[pytz.BaseTzInfo] = pytz.utc,
) -> datetime.datetime:
    """
    Convert any time string/datetime to Asia/Ho_Chi_Minh (UTC+7).

    Supports:
        - ISO 8601 format (with or without timezone)
        - "YYYY-MM-DD HH:MM:SS" format
        - datetime objects

    Args:
        time_str:        Time string or datetime object
        source_timezone: Timezone for naive datetimes (default UTC)

    Returns:
        Localized datetime in Asia/Ho_Chi_Minh
    """
    dt_object = None

    try:
        if isinstance(time_str, datetime.datetime):
            time_str = time_str.isoformat()

        dt_object = parser.isoparse(time_str)

        if dt_object.tzinfo is not None and dt_object.tzinfo.utcoffset(dt_object) is not None:
            pass  # Already timezone-aware
        else:
            if source_timezone:
                dt_object = source_timezone.localize(dt_object)
            else:
                raise ValueError("Cannot localize naive datetime without source_timezone.")

    except ValueError:
        if not validate_time_format(time_str):
            raise ValueError(
                f"Invalid time format: '{time_str}'. Expected ISO or YYYY-MM-DD HH:MM:SS."
            )

        naive_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        if source_timezone:
            dt_object = source_timezone.localize(naive_dt)
        else:
            raise ValueError("Cannot localize naive datetime without source_timezone.")

    target_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return dt_object.astimezone(target_tz)
