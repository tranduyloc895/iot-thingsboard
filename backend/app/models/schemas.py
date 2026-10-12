from typing import List, Optional
from pydantic import BaseModel

class DeviceTelemetry(BaseModel):
    device_id: str
    name: str
    latitude: float
    longitude: float
    water_level_cm: float
    rainfall_mm: float
    temperature_c: float
    status: str  # SAFE, ALERT, WARNING, CRITICAL
    updated_at: str
    road_id: Optional[str] = None
    road_name: Optional[str] = None
    station_node: Optional[str] = None
    segment_idx: Optional[int] = None

class TideHourlyPoint(BaseModel):
    hour: int
    level: float

class TideStation(BaseModel):
    station_id: str
    name: str
    current_level: float
    trend: str  # UP, DOWN, STABLE
    status: str  # STABLE, WARNING, HIGH, CRITICAL
    peak_level: float
    peak_hour: int
    hourly_data: List[TideHourlyPoint]

class SevereLocation(BaseModel):
    id: str
    name: str
    district: str
    water_level_m: float
    severity: str  # ALERT, WARNING, CRITICAL
    minutes_ago: int
    latitude: float
    longitude: float

class RoadNode(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    water_level_cm: float
    status: str  # SAFE, ALERT, WARNING, CRITICAL

class FloodedRoad(BaseModel):
    id: str
    name: str
    district: str
    length_km: float
    severity: str  # SAFE, ALERT, WARNING, CRITICAL
    avg_water_cm: float
    max_water_cm: float
    coordinates: List[List[float]]  # List of [lat, lon]
    nodes: List[RoadNode]

class CitySummary(BaseModel):
    safe_count: int
    alert_count: int
    critical_count: int
    avg_water_level_cm: float
    total_active_devices: int

class DashboardData(BaseModel):
    timestamp: str
    summary: CitySummary
    tides: List[TideStation]
    severe_locations: List[SevereLocation]
    devices: List[DeviceTelemetry]
    roads: List[FloodedRoad] = []
