# -*- coding: utf-8 -*-
"""
DateTime Utilities — Timezone-aware datetime helpers.
Convention: Store UTC in DB, display Asia/Ho_Chi_Minh (UTC+7) for user.
"""
import datetime
from typing import Optional

import pytz
from dateutil import parser


def get_current_time_zone_7(time_zone: str = "Asia/Bangkok") -> datetime.datetime:
    return datetime.datetime.now(pytz.timezone(time_zone))


def get_current_timestamp() -> int:
    current_time = datetime.datetime.now(pytz.timezone("Asia/Bangkok")).astimezone(pytz.utc)
    return int(round(current_time.timestamp()))


def get_current_time() -> datetime.datetime:
    """Get current time in UTC. Used as default for TenantAwareDocument fields."""
    current_time = datetime.datetime.now(pytz.timezone("Asia/Bangkok")).replace()
    return current_time.astimezone(pytz.utc)


def validate_time_format(time_str: str, format_time: str = "%Y-%m-%d %H:%M:%S") -> bool:
    try:
        datetime.datetime.strptime(time_str, format_time)
        return True
    except Exception:
        return False


def convert_to_hcm_time(
    time_str: str | datetime.datetime,
    source_timezone: Optional[pytz.BaseTzInfo] = pytz.utc,
) -> datetime.datetime:
    dt_object = None
    try:
        if isinstance(time_str, datetime.datetime):
            time_str = time_str.isoformat()
        dt_object = parser.isoparse(time_str)
        if dt_object.tzinfo is None or dt_object.tzinfo.utcoffset(dt_object) is None:
            if source_timezone:
                dt_object = source_timezone.localize(dt_object)
            else:
                raise ValueError("Cannot localize naive datetime without source_timezone.")
    except ValueError:
        if not validate_time_format(time_str):
            raise ValueError(f"Invalid time format: '{time_str}'.")
        naive_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        if source_timezone:
            dt_object = source_timezone.localize(naive_dt)
        else:
            raise ValueError("Cannot localize naive datetime without source_timezone.")

    return dt_object.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
