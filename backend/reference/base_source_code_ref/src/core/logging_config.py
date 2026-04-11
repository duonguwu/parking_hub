# -*- coding: utf-8 -*-
"""
Centralized Logging Configuration

Usage:
    from app.core.logging_config import setup_logging
    setup_logging(service="main")          # API server
    setup_logging(service="worker_name")   # Worker process

Features:
    - File log rieng cho tung service: logs/main.log, logs/worker.log
    - RotatingFileHandler: 50MB / file, giu 5 ban
    - Timestamp GMT+7 (Asia/Ho_Chi_Minh)
    - Console + file song song
    - Rate-limit noise tu libraries ben ngoai
"""
import datetime
import logging
import logging.handlers
import os
import time as _t

# Timezone GMT+7
_TZ = datetime.timezone(datetime.timedelta(hours=7))

# Log dir: project_root/logs/
_LOG_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "logs")
)

# Thu vien ben ngoai — chi WARNING tro len
_NOISY_LIBS = (
    "urllib3", "httpx", "httpcore", "grpc", "asyncio",
    "aioredis", "redis", "hpack", "h2", "uvicorn.access",
    "multiprocessing", "concurrent",
)


class VNFormatter(logging.Formatter):
    """Formatter voi timestamp GMT+7."""

    def formatTime(self, record, datefmt=None):  # noqa: N802
        dt = datetime.datetime.fromtimestamp(record.created, tz=_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S") + f",{int(record.msecs):03d}"


def setup_logging(
    service: str = "main",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    max_bytes: int = 50 * 1024 * 1024,  # 50 MB
    backup_count: int = 5,
) -> None:
    """
    Khoi tao logging cho mot service.

    Args:
        service:       "main" | "worker_name" -> logs/{service}.log
        console_level: Level in ra console (default INFO)
        file_level:    Level ghi vao file (default DEBUG)
        max_bytes:     Kich thuoc toi da 1 file log (default 50MB)
        backup_count:  So ban backup giu lai (default 5)
    """
    # Timezone
    os.environ["TZ"] = "Asia/Ho_Chi_Minh"
    try:
        _t.tzset()
    except AttributeError:
        pass  # Windows

    os.makedirs(_LOG_DIR, exist_ok=True)
    log_path = os.path.join(_LOG_DIR, f"{service}.log")

    fmt = VNFormatter("%(asctime)s [%(levelname).1s] %(name)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(console_level)

    # File handler (RotatingFileHandler)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    file_handler.setLevel(file_level)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Giam noise tu thu vien ngoai
    for lib in _NOISY_LIBS:
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        f"Logging started | service={service} | file={log_path} | "
        f"console={logging.getLevelName(console_level)} | "
        f"file_level={logging.getLevelName(file_level)}"
    )
