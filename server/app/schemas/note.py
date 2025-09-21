from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)


class Note(NoteBase):
    id: UUID
    user_id: UUID
    application_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteList(BaseModel):
    notes: List[Note]
    total: int
    page: int
    page_size: int
    total_pages: int
