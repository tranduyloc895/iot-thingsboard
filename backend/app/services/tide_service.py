from typing import List
from ..models.schemas import TideStation

class TideService:
    # No measured tide/forecast feed is configured. Never manufacture a curve.
    unavailable_reason = "Chưa cấu hình nguồn quan trắc và dự báo triều cường."

    @staticmethod
    async def get_tide_data() -> List[TideStation]:
        return []
