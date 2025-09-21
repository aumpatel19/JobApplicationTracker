from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import date


class KPICard(BaseModel):
    total_applications: int
    active_applications: int
    offers: int
    rejections: int


class WeeklySubmission(BaseModel):
    week_start: date
    count: int


class StageFunnelData(BaseModel):
    stage: str
    count: int


class DashboardData(BaseModel):
    kpis: KPICard
    weekly_submissions: List[WeeklySubmission]
    stage_funnel: List[StageFunnelData]
    recent_activity: List[Dict[str, Any]]
