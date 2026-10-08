import re
import asyncio
from urllib.parse import urlsplit

import httpx

from app.core.config import settings

MAX_IMAGE_BYTES = 2 * 1024 * 1024
IMAGE_TYPES = {'image/jpeg', 'image/png'}
SOURCE_PATH = re.compile(r'/api/cam/[a-f0-9]+/image')
_slots = asyncio.Semaphore(8)


class SnapshotUnavailable(Exception):
    pass


def allowed_source(url: str) -> bool:
    parts = urlsplit(url)
    return (parts.scheme == 'https' and parts.netloc == 'argosatlas.com'
            and SOURCE_PATH.fullmatch(parts.path) is not None
            and not parts.query and not parts.fragment)


async def fetch_snapshot(url: str) -> tuple[bytes, str]:
    if not allowed_source(url):
        raise SnapshotUnavailable('Invalid camera source')
    try:
        async with _slots:
            async with httpx.AsyncClient(timeout=settings.TRAFFIC_CAMERA_HTTP_TIMEOUT_SECONDS,
                                         follow_redirects=False, trust_env=False) as client:
                async with client.stream('GET', url) as response:
                    media_type = response.headers.get('content-type', '').split(';', 1)[0].lower().strip()
                    if response.status_code != 200 or media_type not in IMAGE_TYPES:
                        raise SnapshotUnavailable('Camera source unavailable')
                    if int(response.headers.get('content-length', '0')) > MAX_IMAGE_BYTES:
                        raise SnapshotUnavailable('Camera image too large')
                    image = bytearray()
                    async for chunk in response.aiter_bytes():
                        image.extend(chunk)
                        if len(image) > MAX_IMAGE_BYTES:
                            raise SnapshotUnavailable('Camera image too large')
                    if not image:
                        raise SnapshotUnavailable('Empty camera image')
                    return bytes(image), media_type
    except (httpx.HTTPError, ValueError) as exc:
        raise SnapshotUnavailable('Camera source unavailable') from exc
