from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    application_id: Optional[UUID] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    linkedin: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    application_id: Optional[UUID] = None


class Contact(ContactBase):
    id: UUID
    user_id: UUID
    application_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactList(BaseModel):
    contacts: List[Contact]
    total: int
    page: int
    page_size: int
    total_pages: int
