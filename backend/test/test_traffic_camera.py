import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from app.api.auth.jwt_manager import create_access_token
from app.core.config import settings
from app.api.traffic_camera.traffic_camera_utils import cameras_along_route, cameras_in_bbox
from app.services.traffic_camera.catalog import CATALOG_PATH, load_cameras


@pytest.mark.asyncio
async def test_camera_gate_and_validation(monkeypatch):
    token = create_access_token({'sub': 'camera-test', 'role': 'customer'})
    monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_ENABLED', False)
    monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_POC_IMAGES_ENABLED', False)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test',
                           cookies={'access_token': token}) as client:
        assert (await client.get('/traffic-cameras/availability')).json()['data'] == {
            'enabled': False, 'images_enabled': False,
        }
        assert (await client.get('/traffic-cameras', params={
            'west': 106.6, 'south': 10.7, 'east': 106.8, 'north': 10.9,
        })).status_code == 404

        monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_ENABLED', True)
        response = await client.get('/traffic-cameras', params={
            'west': 106.6, 'south': 10.7, 'east': 106.8, 'north': 10.9,
        })
        assert response.status_code == 200
        assert response.json()['data']['cameras']
        assert (await client.get('/traffic-cameras', params={
            'west': 106.6, 'south': 10.7, 'east': 107.8, 'north': 10.9,
        })).status_code == 422
        assert (await client.get('/traffic-cameras/any/snapshot')).status_code == 503
        assert (await client.post('/traffic-cameras/along-route', json={
            'route': [[10.79, 106.68], [10.79, 106.70]],
        })).status_code == 200
        assert (await client.post('/traffic-cameras/along-route', json={
            'route': [[10.79, 106.68], [10.79, 107.70]],
        })).status_code == 422


@pytest.mark.asyncio
async def test_camera_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        assert (await client.get('/traffic-cameras/availability')).status_code == 401


def test_catalog_never_exposes_upstream_urls():
    assert CATALOG_PATH.is_relative_to(CATALOG_PATH.parents[2])
    assert CATALOG_PATH.parts[-4:] == ('services', 'traffic_camera', 'data', 'cameras.json')
    assert len(load_cameras()) == 796
    cameras = cameras_in_bbox(106.6, 10.7, 106.8, 10.9)
    assert cameras
    assert all('SnapshotUrl' not in camera and 'FallbackSnapshotUrl' not in camera for camera in cameras)
    assert any(camera['snapshot_available'] for camera in cameras)


@pytest.mark.asyncio
async def test_snapshot_gate_and_source(monkeypatch):
    camera_id = '662b86c41afb9c00172dd31c'
    token = create_access_token({'sub': 'camera-test', 'role': 'customer'})
    monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_ENABLED', True)
    monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_POC_IMAGES_ENABLED', True)

    async def image(_url):
        return b'jpeg-image', 'image/jpeg'

    monkeypatch.setattr('app.api.traffic_camera.traffic_camera_views.fetch_snapshot', image)
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test',
                           cookies={'access_token': token}) as client:
        assert (await client.get('/traffic-cameras/availability')).json()['data']['images_enabled'] is True
        assert (await client.get('/traffic-cameras/missing/snapshot')).status_code == 404
        response = await client.get(f'/traffic-cameras/{camera_id}/snapshot')
        assert response.status_code == 200
        assert response.content == b'jpeg-image'
        assert response.headers['cache-control'] == 'no-store'
        monkeypatch.setattr(settings, 'TRAFFIC_CAMERA_POC_IMAGES_ENABLED', False)
        assert (await client.get(f'/traffic-cameras/{camera_id}/snapshot')).status_code == 503


@pytest.mark.asyncio
async def test_snapshot_source_rejects_invalid_responses(monkeypatch):
    import httpx
    from app.services.traffic_camera import snapshot as source

    assert not source.allowed_source('https://argosatlas.com.evil.test/api/cam/abc/image')
    assert not source.allowed_source('https://argosatlas.com/api/cam/abc/image?next=1')

    original_client = httpx.AsyncClient

    def mocked_client(handler):
        return original_client(transport=httpx.MockTransport(handler))

    for status, headers, content in (
        (302, {'location': 'https://example.org/'}, b''),
        (200, {'content-type': 'text/html'}, b'no'),
        (200, {'content-type': 'image/jpeg'}, b'x' * (source.MAX_IMAGE_BYTES + 1)),
    ):
        client = mocked_client(lambda request: httpx.Response(status, headers=headers, content=content))
        monkeypatch.setattr(source.httpx, 'AsyncClient', lambda **kwargs: client)
        with pytest.raises(source.SnapshotUnavailable):
            await source.fetch_snapshot('https://argosatlas.com/api/cam/abc/image')

    client = mocked_client(lambda request: httpx.Response(200, headers={'content-type': 'image/jpeg'}, content=b'jpeg-image'))
    monkeypatch.setattr(source.httpx, 'AsyncClient', lambda **kwargs: client)
    assert await source.fetch_snapshot('https://argosatlas.com/api/cam/abc/image') == (b'jpeg-image', 'image/jpeg')


def test_route_projection_is_ordered():
    route = [(10.79, 106.68), (10.79, 106.70)]
    cameras = cameras_along_route(route)
    assert all(camera['distance_to_route_m'] <= 250 for camera in cameras)
    assert [camera['distance_from_start_m'] for camera in cameras] == sorted(camera['distance_from_start_m'] for camera in cameras)
