# -*- coding: utf-8 -*-
"""
Centralized Logging Configuration — GMT+7, RotatingFile.

Usage:
    from app.core.logging_config import setup_logging
    setup_logging(service="main")
    setup_logging(service="worker_matching")
"""
import datetime
import logging
import logging.handlers
import os
import time as _t

_TZ = datetime.timezone(datetime.timedelta(hours=7))

_LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "logs")
)

_NOISY_LIBS = (
    "urllib3", "httpx", "httpcore", "grpc", "asyncio",
    "aioredis", "redis", "hpack", "h2", "uvicorn.access",
    "multiprocessing", "concurrent",
)


class VNFormatter(logging.Formatter):
    """Formatter with GMT+7 timestamp."""

    def formatTime(self, record, datefmt=None):  # noqa: N802
        dt = datetime.datetime.fromtimestamp(record.created, tz=_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + f",{int(record.msecs):03d}"


def setup_logging(
    service: str = "main",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    max_bytes: int = 50 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    os.environ["TZ"] = "Asia/Ho_Chi_Minh"
    try:
        _t.tzset()
    except AttributeError:
        pass

    os.makedirs(_LOG_DIR, exist_ok=True)
    log_path = os.path.join(_LOG_DIR, f"{service}.log")

    fmt = VNFormatter("%(asctime)s [%(levelname).1s] %(name)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(console_level)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path, mode="a", maxBytes=max_bytes,
        backupCount=backup_count, encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    for lib in _NOISY_LIBS:
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging started | service={service} | file={log_path}"
    )
