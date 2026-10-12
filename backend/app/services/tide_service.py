import math
from datetime import datetime
from typing import List
from ..models.schemas import TideStation, TideHourlyPoint

class TideService:
    @staticmethod
    async def get_tide_data() -> List[TideStation]:
        """
        Lấy thông tin thủy triều tại 4 trạm thủy văn quan trắc ngập trọng điểm của TP.HCM:
        1. Trạm Cảng Sài Gòn (Phú An - Sông Sài Gòn)
        2. Trạm Nhà Bè (Ngã ba sông Đồng Nai - Lòng Tàu)
        3. Trạm Kênh Nhiêu Lộc - Thị Nghè (Lưu vực trung tâm)
        4. Trạm Kênh Đôi - Kênh Tẻ (Lưu vực Tây Nam TP.HCM)
        """
        now = datetime.now()
        current_hour = now.hour
        
        # 1. Trạm Sông Sài Gòn (Cảng / Phú An)
        saigon_points: List[TideHourlyPoint] = []
        for h in range(25):
            val = 0.9 + 0.55 * math.sin((h - 5) * math.pi / 6) + 0.1 * math.sin((h - 2) * math.pi / 3)
            saigon_points.append(TideHourlyPoint(hour=h, level=round(max(0.4, val), 2)))
        
        current_sg = saigon_points[current_hour].level
        sg_peak = max(p.level for p in saigon_points)
        sg_peak_h = next(p.hour for p in saigon_points if p.level == sg_peak)
        sg_trend = "UP" if current_hour < sg_peak_h else "DOWN"
        sg_status = "HIGH" if current_sg >= 1.4 else ("WARNING" if current_sg >= 1.2 else "STABLE")

        # 2. Trạm Nhà Bè (Đồng Điền)
        nhabe_points: List[TideHourlyPoint] = []
        for h in range(25):
            val = 0.85 + 0.48 * math.sin((h - 4.5) * math.pi / 6) + 0.08 * math.sin((h - 1.5) * math.pi / 3)
            nhabe_points.append(TideHourlyPoint(hour=h, level=round(max(0.35, val), 2)))
        
        current_nb = nhabe_points[current_hour].level
        nb_peak = max(p.level for p in nhabe_points)
        nb_peak_h = next(p.hour for p in nhabe_points if p.level == nb_peak)
        nb_trend = "UP" if current_hour < nb_peak_h else "DOWN"
        nb_status = "HIGH" if current_nb >= 1.4 else ("WARNING" if current_nb >= 1.2 else "STABLE")

        # 3. Trạm Kênh Nhiêu Lộc - Thị Nghè (Thị Nghè / Cầu Bông)
        nhieuloc_points: List[TideHourlyPoint] = []
        for h in range(25):
            val = 0.75 + 0.42 * math.sin((h - 5.2) * math.pi / 6) + 0.09 * math.sin((h - 2.2) * math.pi / 3)
            nhieuloc_points.append(TideHourlyPoint(hour=h, level=round(max(0.3, val), 2)))

        current_nl = nhieuloc_points[current_hour].level
        nl_peak = max(p.level for p in nhieuloc_points)
        nl_peak_h = next(p.hour for p in nhieuloc_points if p.level == nl_peak)
        nl_trend = "UP" if current_hour < nl_peak_h else "DOWN"
        nl_status = "HIGH" if current_nl >= 1.35 else ("WARNING" if current_nl >= 1.15 else "STABLE")

        # 4. Trạm Kênh Đôi - Kênh Tẻ (Chợ Lớn / Q.8)
        kenhdoi_points: List[TideHourlyPoint] = []
        for h in range(25):
            val = 0.88 + 0.52 * math.sin((h - 4.8) * math.pi / 6) + 0.1 * math.sin((h - 1.8) * math.pi / 3)
            kenhdoi_points.append(TideHourlyPoint(hour=h, level=round(max(0.35, val), 2)))

        current_kd = kenhdoi_points[current_hour].level
        kd_peak = max(p.level for p in kenhdoi_points)
        kd_peak_h = next(p.hour for p in kenhdoi_points if p.level == kd_peak)
        kd_trend = "UP" if current_hour < kd_peak_h else "DOWN"
        kd_status = "HIGH" if current_kd >= 1.4 else ("WARNING" if current_kd >= 1.2 else "STABLE")

        return [
            TideStation(
                station_id="saigon_port",
                name="SAIGON RIVER (Port)",
                current_level=current_sg,
                trend=sg_trend,
                status=sg_status,
                peak_level=sg_peak,
                peak_hour=sg_peak_h,
                hourly_data=saigon_points
            ),
            TideStation(
                station_id="nha_be",
                name="NHA BE (Dong Dien)",
                current_level=current_nb,
                trend=nb_trend,
                status=nb_status,
                peak_level=nb_peak,
                peak_hour=nb_peak_h,
                hourly_data=nhabe_points
            ),
            TideStation(
                station_id="nhieu_loc",
                name="NHIEU LOC - THI NGHE",
                current_level=current_nl,
                trend=nl_trend,
                status=nl_status,
                peak_level=nl_peak,
                peak_hour=nl_peak_h,
                hourly_data=nhieuloc_points
            ),
            TideStation(
                station_id="kenh_doi",
                name="KENH DOI - KENH TE",
                current_level=current_kd,
                trend=kd_trend,
                status=kd_status,
                peak_level=kd_peak,
                peak_hour=kd_peak_h,
                hourly_data=kenhdoi_points
            )
        ]
