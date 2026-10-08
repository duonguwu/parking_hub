import json
from math import isfinite
from functools import lru_cache
from pathlib import Path

from app.services.traffic_camera.snapshot import allowed_source

CATALOG_PATH = Path(__file__).resolve().parent / 'data' / 'cameras.json'


@lru_cache(maxsize=1)
def load_cameras() -> tuple[dict, ...]:
    with CATALOG_PATH.open(encoding='utf-8') as stream:
        records = json.load(stream)
    return tuple(
        c for c in records
        if c.get('id') and type(c.get('lat')) in (int, float)
        and type(c.get('lng')) in (int, float)
        and isfinite(c['lat']) and isfinite(c['lng'])
        and 8 <= c['lat'] <= 12 and 105 <= c['lng'] <= 108
    )


def public_camera(camera: dict, **extra: int) -> dict:
    return {
        'id': camera['id'], 'name': camera.get('name') or camera['id'],
        'lat': camera['lat'], 'lng': camera['lng'],
        'district': camera.get('district') or '',
        'snapshot_available': allowed_source(camera.get('snapshot_url') or ''),
        **extra,
    }


def find_camera(camera_id: str) -> dict | None:
    return next((camera for camera in load_cameras() if camera['id'] == camera_id), None)
