# -*- coding: utf-8 -*-
"""
OSM Client — Wrapper quanh OSRM routing.

Fallback Haversine nếu OSRM timeout/fail → matching engine vẫn hoạt động.
Cache routes trong Redis (key: origin+dest rounded, TTL=1h).

Urban VN: avg speed ~25 km/h peak, ~35 km/h off-peak.
Haversine (straight-line) → multiply by 1.3-1.4 để approximate road distance.
"""
import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import httpx

from app.core.config import settings
from app.services.shared.redis_client import redis_client

logger = logging.getLogger(__name__)

# Urban VN defaults
URBAN_AVG_SPEED_KMH = 25.0
ROAD_DISTANCE_FACTOR = 1.35          # Haversine → road distance approx


@dataclass
class LatLng:
    lat: float
    lng: float

    def to_coords(self) -> List[float]:
        """[lng, lat] — OSRM format."""
        return [self.lng, self.lat]

    def cache_key(self) -> str:
        # Round to ~100m precision for caching
        return f"{round(self.lat, 3)},{round(self.lng, 3)}"


@dataclass
class RouteInfo:
    duration_seconds: float
    distance_meters: float
    confidence: float                 # 1.0=OSRM, 0.5=Haversine fallback
    geometry: Optional[str] = None    # polyline (OSRM only)


@dataclass
class Matrix:
    durations: List[List[float]]      # [origin_idx][dest_idx] seconds
    distances: List[List[float]]      # meters
    confidence: float                 # lowest confidence of any pair
    sources_count: int = 0
    destinations_count: int = 0


def haversine_meters(a: LatLng, b: LatLng) -> float:
    """Haversine distance in meters."""
    R = 6371000.0  # earth radius
    lat1, lat2 = math.radians(a.lat), math.radians(b.lat)
    dlat = lat2 - lat1
    dlng = math.radians(b.lng - a.lng)
    x = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * R * math.asin(math.sqrt(x))


def _haversine_route(origin: LatLng, destination: LatLng) -> RouteInfo:
    """Fallback when OSRM unavailable — estimate road distance + time."""
    straight = haversine_meters(origin, destination)
    road = straight * ROAD_DISTANCE_FACTOR
    duration_sec = (road / 1000.0) / URBAN_AVG_SPEED_KMH * 3600
    return RouteInfo(
        duration_seconds=duration_sec,
        distance_meters=road,
        confidence=0.5,
    )


class OSMClient:
    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                timeout=settings.OSM_HTTP_TIMEOUT_SECONDS,
                headers={"User-Agent": "WashMind/0.1 (backend)"},
            )
        return self._http

    async def close(self) -> None:
        if self._http is not None and not self._http.is_closed:
            await self._http.aclose()

    # ── Single route ──────────────────────────────────────────────

    async def get_route(self, origin: LatLng, destination: LatLng) -> RouteInfo:
        cache_key = f"route:{origin.cache_key()}->{destination.cache_key()}"

        # Try cache
        try:
            cached = await redis_client.get_json(cache_key)
            if cached:
                return RouteInfo(**cached)
        except Exception as e:
            logger.debug(f"Redis cache miss/error: {e}")

        # Try OSRM
        try:
            url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{origin.lng},{origin.lat};{destination.lng},{destination.lat}"
            params = {"overview": "false", "alternatives": "false"}
            http = await self._get_http()
            resp = await http.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok" or not data.get("routes"):
                raise ValueError(f"OSRM error: {data.get('code')}")
            r = data["routes"][0]
            info = RouteInfo(
                duration_seconds=float(r["duration"]),
                distance_meters=float(r["distance"]),
                confidence=1.0,
            )
        except Exception as e:
            logger.warning(f"OSRM failed, using Haversine fallback: {e}")
            info = _haversine_route(origin, destination)

        # Cache result
        try:
            await redis_client.set_json(
                cache_key,
                {"duration_seconds": info.duration_seconds,
                 "distance_meters": info.distance_meters,
                 "confidence": info.confidence},
                ttl_seconds=settings.OSM_ROUTE_CACHE_TTL_SECONDS,
            )
        except Exception as e:
            logger.debug(f"Redis cache set failed: {e}")

        return info

    # ── Matrix (batch routing) ────────────────────────────────────

    async def get_matrix(
        self, origins: List[LatLng], destinations: List[LatLng]
    ) -> Matrix:
        """
        OSRM /table endpoint — batch compute N×M routing.
        Critical for matching: 1 call for all candidates instead of N calls.
        """
        if not origins or not destinations:
            return Matrix(durations=[], distances=[], confidence=1.0)

        try:
            all_points = origins + destinations
            coords = ";".join(f"{p.lng},{p.lat}" for p in all_points)
            src_idx = ";".join(str(i) for i in range(len(origins)))
            dst_idx = ";".join(str(i + len(origins)) for i in range(len(destinations)))

            url = f"{settings.OSRM_BASE_URL}/table/v1/driving/{coords}"
            params = {
                "sources": src_idx,
                "destinations": dst_idx,
                "annotations": "duration,distance",
            }
            http = await self._get_http()
            resp = await http.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                raise ValueError(f"OSRM table error: {data.get('code')}")

            durations = data.get("durations") or []
            distances = data.get("distances") or []

            # Some public OSRMs don't return distances — fallback to Haversine estimate
            if not distances or any(d is None for row in distances for d in row):
                distances = [
                    [haversine_meters(o, d) * ROAD_DISTANCE_FACTOR for d in destinations]
                    for o in origins
                ]

            return Matrix(
                durations=durations,
                distances=distances,
                confidence=1.0,
                sources_count=len(origins),
                destinations_count=len(destinations),
            )
        except Exception as e:
            logger.warning(f"OSRM matrix failed, using Haversine fallback: {e}")
            # Per-pair Haversine estimation
            durations = [
                [_haversine_route(o, d).duration_seconds for d in destinations]
                for o in origins
            ]
            distances = [
                [haversine_meters(o, d) * ROAD_DISTANCE_FACTOR for d in destinations]
                for o in origins
            ]
            return Matrix(
                durations=durations,
                distances=distances,
                confidence=0.5,
                sources_count=len(origins),
                destinations_count=len(destinations),
            )


# Singleton
osm_client = OSMClient()
