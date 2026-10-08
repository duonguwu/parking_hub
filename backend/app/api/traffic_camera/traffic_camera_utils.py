from math import cos, hypot, pi

from app.services.traffic_camera.catalog import load_cameras, public_camera


def cameras_in_bbox(west: float, south: float, east: float, north: float) -> list[dict]:
    cameras = (c for c in load_cameras() if west <= c['lng'] <= east and south <= c['lat'] <= north)
    return [public_camera(c) for c in cameras][:500]


def cameras_along_route(route: list[tuple[float, float]], max_distance_m: float = 250) -> list[dict]:
    lat_scale = 6371000 * pi / 180
    lng_scale = lat_scale * cos(sum(p[0] for p in route) / len(route) * pi / 180)
    points = [(lng * lng_scale, lat * lat_scale) for lat, lng in route]
    segments, traveled = [], 0.0
    for start, end in zip(points, points[1:]):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = hypot(dx, dy)
        segments.append((start, dx, dy, length, traveled))
        traveled += length
    result = []
    for camera in load_cameras():
        x, y = camera['lng'] * lng_scale, camera['lat'] * lat_scale
        nearest = (float('inf'), 0.0)
        for (sx, sy), dx, dy, length, offset in segments:
            fraction = min(1.0, max(0.0, ((x - sx) * dx + (y - sy) * dy) / (length * length))) if length else 0.0
            distance = hypot(x - sx - fraction * dx, y - sy - fraction * dy)
            if distance < nearest[0]:
                nearest = (distance, offset + fraction * length)
        if nearest[0] <= max_distance_m:
            result.append(public_camera(
                camera, distance_to_route_m=round(nearest[0]),
                distance_from_start_m=round(nearest[1]),
            ))
    return sorted(result, key=lambda c: c['distance_from_start_m'])[:100]
