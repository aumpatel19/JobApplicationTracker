from pydantic import BaseModel, Field
from datetime import datetime, date
from uuid import UUID
from typing import Optional, List
from ..models.application import ApplicationStage, ApplicationPriority, ApplicationSource, EmploymentType


class ApplicationBase(BaseModel):
    role_title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[EmploymentType] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    source: ApplicationSource = ApplicationSource.OTHER
    stage: ApplicationStage = ApplicationStage.DRAFT
    priority: ApplicationPriority = ApplicationPriority.MEDIUM
    next_action: Optional[str] = None
    next_action_due: Optional[date] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    role_title: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    employment_type: Optional[EmploymentType] = None
    salary_range: Optional[str] = Field(None, max_length=100)
    source: Optional[ApplicationSource] = None
    stage: Optional[ApplicationStage] = None
    priority: Optional[ApplicationPriority] = None
    next_action: Optional[str] = None
    next_action_due: Optional[date] = None


class Application(ApplicationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationList(BaseModel):
    applications: List[Application]
    total: int
    page: int
    page_size: int
    total_pages: int


class ApplicationStageUpdate(BaseModel):
    stage: ApplicationStage
