from math import cos, hypot, isfinite, radians
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from app.api.auth.dependencies import get_current_user
from app.api.shared.common_utils import api_response
from app.api.traffic_camera.traffic_camera_utils import cameras_along_route, cameras_in_bbox
from app.core.config import settings
from app.services.traffic_camera.catalog import find_camera
from app.services.traffic_camera.snapshot import SnapshotUnavailable, fetch_snapshot

traffic_camera_router = APIRouter(
    prefix='/traffic-cameras', tags=['Traffic Cameras'],
    dependencies=[Depends(get_current_user)],
)


class RouteRequest(BaseModel):
    route: list[tuple[float, float]] = Field(..., min_length=2, max_length=500)


@traffic_camera_router.get('/availability')
async def availability():
    return api_response('retrieved', 'traffic cameras', {
        'enabled': settings.TRAFFIC_CAMERA_ENABLED,
        'images_enabled': settings.TRAFFIC_CAMERA_ENABLED and settings.TRAFFIC_CAMERA_POC_IMAGES_ENABLED,
    })


def require_enabled():
    if not settings.TRAFFIC_CAMERA_ENABLED:
        raise HTTPException(status_code=404, detail='Camera unavailable')


@traffic_camera_router.get('')
async def list_cameras(
    west: float = Query(..., ge=-180, le=180),
    south: float = Query(..., ge=-90, le=90),
    east: float = Query(..., ge=-180, le=180),
    north: float = Query(..., ge=-90, le=90),
):
    require_enabled()
    if not all(isfinite(value) for value in (west, south, east, north)):
        raise HTTPException(status_code=422, detail='Invalid viewport')
    if west >= east or south >= north or east-west > 0.5 or north-south > 0.5:
        raise HTTPException(status_code=422, detail='Invalid viewport')
    return api_response('retrieved', 'traffic cameras', {'cameras': cameras_in_bbox(west, south, east, north)})


@traffic_camera_router.post('/along-route')
async def along_route(body: RouteRequest):
    require_enabled()
    if any(not (isfinite(lat) and isfinite(lng) and 8 <= lat <= 12 and 105 <= lng <= 108)
           for lat, lng in body.route):
        raise HTTPException(status_code=422, detail='Invalid route coordinates')
    length_km = sum(
        hypot((a[0] - b[0]) * 111, (a[1] - b[1]) * 111 * cos(radians((a[0] + b[0]) / 2)))
        for a, b in zip(body.route, body.route[1:])
    )
    if length_km > 60:
        raise HTTPException(status_code=422, detail='Route too long')
    return api_response('retrieved', 'traffic cameras', {'cameras': cameras_along_route(body.route)})


@traffic_camera_router.get('/{camera_id}/snapshot')
async def snapshot(camera_id: str):
    require_enabled()
    if not settings.TRAFFIC_CAMERA_POC_IMAGES_ENABLED:
        raise HTTPException(status_code=503, detail='Camera images disabled')
    camera = find_camera(camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail='Camera not found')
    source = camera.get('snapshot_url')
    if not source:
        raise HTTPException(status_code=503, detail='Camera image unavailable')
    try:
        image, media_type = await fetch_snapshot(source)
    except SnapshotUnavailable as exc:
        raise HTTPException(status_code=503, detail='Camera image unavailable') from exc
    return Response(image, media_type=media_type, headers={'Cache-Control': 'no-store'})
