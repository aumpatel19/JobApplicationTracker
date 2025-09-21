import uuid
import enum
from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class TimelineEventType(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    STAGE_CHANGED = "stage_changed"
    NOTE_ADDED = "note_added"
    CONTACT_ADDED = "contact_added"
    FILE_ADDED = "file_added"


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False, index=True)
    
    type = Column(String(50), nullable=False)
    payload = Column(JSON)  # Store additional event data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    application = relationship("Application", back_populates="timeline_events")
