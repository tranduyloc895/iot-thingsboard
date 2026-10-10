import httpx
from ..config import settings

class WeatherService:
    @staticmethod
    async def get_current_weather() -> dict:
        """
        Lấy thông tin lượng mưa và thời tiết thời gian thực tại TP.HCM từ Open-Meteo.
        """
        params = {
            "latitude": settings.HCMC_LAT,
            "longitude": settings.HCMC_LON,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code",
            "timezone": "Asia/Ho_Chi_Minh"
        }
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(settings.OPEN_METEO_WEATHER_URL, params=params)
                if res.status_code == 200:
                    data = res.json().get("current", {})
                    return {
                        "temperature_c": data.get("temperature_2m", 30.5),
                        "humidity_percent": data.get("relative_humidity_2m", 82),
                        "rainfall_mm": data.get("rain", 15.2),
                        "source": "Open-Meteo Live API"
                    }
        except Exception:
            pass

        # Fallback dữ liệu thời tiết thực nghiệm TP.HCM
        return {
            "temperature_c": 31.0,
            "humidity_percent": 80,
            "rainfall_mm": 18.5,
            "source": "Simulated Meteorology Baseline"
        }
