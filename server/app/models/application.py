import uuid
import enum
from sqlalchemy import Column, String, DateTime, Date, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class ApplicationStage(str, enum.Enum):
    DRAFT = "Draft"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"


class ApplicationPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ApplicationSource(str, enum.Enum):
    REFERRAL = "Referral"
    LINKEDIN = "LinkedIn"
    COMPANY_WEBSITE = "Company Website"
    JOB_BOARD = "Job Board"
    RECRUITER = "Recruiter"
    OTHER = "Other"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    role_title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    employment_type = Column(Enum(EmploymentType))
    salary_range = Column(String(100))
    
    # Application metadata
    source = Column(Enum(ApplicationSource), default=ApplicationSource.OTHER)
    stage = Column(Enum(ApplicationStage), default=ApplicationStage.DRAFT, index=True)
    priority = Column(Enum(ApplicationPriority), default=ApplicationPriority.MEDIUM, index=True)
    
    # Action tracking
    next_action = Column(Text)
    next_action_due = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    contacts = relationship("Contact", back_populates="application", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="application", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="application", cascade="all, delete-orphan")
    files = relationship("File", back_populates="application", cascade="all, delete-orphan")
