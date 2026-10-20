import asyncio
import logging
import math
import time
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

class WeatherService:
    _lock = asyncio.Lock()
    _cached = None
    _expires = 0.0

    @classmethod
    async def get_current_weather(cls) -> dict:
        async with cls._lock:
            if cls._cached is not None and time.monotonic() < cls._expires:
                return dict(cls._cached)
            result = {"temperature_c": None, "humidity_percent": None,
                      "rainfall_mm": None, "source": "Open-Meteo", "error": None}
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    response = await client.get(settings.OPEN_METEO_WEATHER_URL, params={
                        "latitude": settings.HCMC_LAT, "longitude": settings.HCMC_LON,
                        "current": "temperature_2m,relative_humidity_2m,rain",
                        "timezone": "Asia/Ho_Chi_Minh",
                    })
                    response.raise_for_status()
                    current = response.json()["current"]
                    for target, key in (("temperature_c", "temperature_2m"),
                                        ("humidity_percent", "relative_humidity_2m"),
                                        ("rainfall_mm", "rain")):
                        value = float(current[key])
                        if not math.isfinite(value):
                            raise ValueError("invalid weather measurement")
                        result[target] = value
                    result["updated_at"] = current["time"]
            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                logger.warning("Weather fetch failed: %s", type(exc).__name__)
                result.update(temperature_c=None, humidity_percent=None, rainfall_mm=None,
                              error="Không lấy được thời tiết từ Open-Meteo. Đang thử lại.")
            cls._cached = result
            cls._expires = time.monotonic() + (15 if result["error"] else 60)
            return dict(result)
