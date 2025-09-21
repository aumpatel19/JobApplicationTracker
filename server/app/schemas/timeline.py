from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Any, Dict, List


class TimelineEvent(BaseModel):
    id: UUID
    application_id: UUID
    type: str
    payload: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class TimelineEventList(BaseModel):
    events: List[TimelineEvent]
    total: int
