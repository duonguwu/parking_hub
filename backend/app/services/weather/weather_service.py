# -*- coding: utf-8 -*-
"""
Weather Service — Open-Meteo wrapper.

Cache theo vị trí round tới 1 quận (~0.01 deg = ~1.1km) trong 15 phút.
VN Q1 có 50 gara đều share cùng weather.

Fallback: fail-silent — matching tiếp tục với weather=clear default.
"""
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

import httpx

from app.core.config import settings
from app.services.shared.redis_client import redis_client

logger = logging.getLogger(__name__)


@dataclass
class WeatherSnapshot:
    precipitation_mm: float = 0.0         # current hour precipitation
    precipitation_mm_last_hour: float = 0.0
    temperature_c: float = 30.0           # VN default
    condition: str = "clear"              # clear | drizzle | rain | storm | unknown

    @property
    def is_raining(self) -> bool:
        return self.precipitation_mm > 0.5

    @property
    def is_drizzling(self) -> bool:
        return 0.1 < self.precipitation_mm <= 0.5


def _weather_code_to_condition(code: int) -> str:
    # Open-Meteo WMO code → human label
    if code == 0:
        return "clear"
    if code in (1, 2, 3):
        return "partly_cloudy"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57):
        return "drizzle"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    if code in (95, 96, 99):
        return "storm"
    return "unknown"


class WeatherService:
    def __init__(self):
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(
                timeout=settings.WEATHER_HTTP_TIMEOUT_SECONDS,
            )
        return self._http

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def current(self, lat: float, lng: float) -> WeatherSnapshot:
        """Current weather at (lat, lng). Cached 15 min per ~1.1km grid cell."""
        # Round to 0.01 deg grid cell
        key = f"weather:{round(lat, 2)}:{round(lng, 2)}"

        try:
            cached = await redis_client.get_json(key)
            if cached:
                return WeatherSnapshot(**cached)
        except Exception:
            pass

        try:
            http = await self._get_http()
            resp = await http.get(
                settings.OPEN_METEO_BASE_URL,
                params={
                    "latitude": lat,
                    "longitude": lng,
                    "current": "temperature_2m,precipitation,weather_code",
                    "past_hours": 1,
                    "hourly": "precipitation",
                    "forecast_hours": 1,
                    "timezone": "Asia/Ho_Chi_Minh",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            cur = data.get("current", {})
            code = int(cur.get("weather_code", 0))
            snap = WeatherSnapshot(
                precipitation_mm=float(cur.get("precipitation", 0) or 0),
                temperature_c=float(cur.get("temperature_2m", 30) or 30),
                condition=_weather_code_to_condition(code),
            )

            # Past-hour precipitation (for "surge demand after rain" detection)
            hourly = data.get("hourly", {})
            past_precip = hourly.get("precipitation", [])
            if past_precip:
                snap.precipitation_mm_last_hour = float(past_precip[0] or 0)
        except Exception as e:
            logger.warning(f"Open-Meteo failed, default clear: {e}")
            snap = WeatherSnapshot()

        try:
            await redis_client.set_json(
                key, asdict(snap), ttl_seconds=settings.WEATHER_CACHE_TTL_SECONDS,
            )
        except Exception:
            pass

        return snap

    async def at(self, lat: float, lng: float, at_time: datetime) -> WeatherSnapshot:
        """
        Weather at future time. For MVP: return current (at_time within 1h).
        Future: use hourly forecast.
        """
        return await self.current(lat, lng)


# Singleton
weather_service = WeatherService()
