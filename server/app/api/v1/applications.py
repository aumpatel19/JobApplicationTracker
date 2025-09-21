from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID
from typing import Optional
from datetime import datetime

from ...db.session import get_db
from ...models.user import User
from ...models.application import Application, ApplicationStage, ApplicationPriority, ApplicationSource
from ...models.timeline_event import TimelineEvent, TimelineEventType
from ...schemas.application import (
    ApplicationCreate, ApplicationUpdate, Application as ApplicationSchema,
    ApplicationList, ApplicationStageUpdate
)
from ...core.deps import get_current_user

router = APIRouter()


def create_timeline_event(db: Session, application_id: UUID, event_type: str, payload: dict = None):
    """Create a timeline event for an application."""
    event = TimelineEvent(
        application_id=application_id,
        type=event_type,
        payload=payload or {}
    )
    db.add(event)


@router.get("", response_model=ApplicationList)
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search in role_title and company"),
    stage: Optional[ApplicationStage] = Query(None, description="Filter by stage"),
    priority: Optional[ApplicationPriority] = Query(None, description="Filter by priority"),
    source: Optional[ApplicationSource] = Query(None, description="Filter by source"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get user's applications with filtering, search, and pagination."""
    query = db.query(Application).filter(Application.user_id == current_user.id)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Application.role_title.ilike(search_term),
                Application.company.ilike(search_term)
            )
        )
    
    if stage:
        query = query.filter(Application.stage == stage)
    
    if priority:
        query = query.filter(Application.priority == priority)
    
    if source:
        query = query.filter(Application.source == source)
    
    # Apply sorting
    sort_column = getattr(Application, sort_by, Application.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    applications = query.offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return ApplicationList(
        applications=applications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=ApplicationSchema)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new application."""
    application = Application(**application_data.model_dump(), user_id=current_user.id)
    db.add(application)
    db.flush()
    
    # Create timeline event
    create_timeline_event(
        db, application.id, TimelineEventType.CREATED.value,
        {"role_title": application.role_title, "company": application.company}
    )
    
    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationSchema)
def get_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific application."""
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.put("/{application_id}", response_model=ApplicationSchema)
def update_application(
    application_id: UUID,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an application."""
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Track stage changes
    old_stage = application.stage
    update_data = application_data.model_dump(exclude_unset=True)
    
    # Update fields
    for field, value in update_data.items():
        setattr(application, field, value)
    
    application.updated_at = datetime.utcnow()
    
    # Create timeline event for stage change
    if "stage" in update_data and old_stage != application.stage:
        create_timeline_event(
            db, application.id, TimelineEventType.STAGE_CHANGED.value,
            {"old_stage": old_stage.value, "new_stage": application.stage.value}
        )
    else:
        # General update event
        create_timeline_event(
            db, application.id, TimelineEventType.UPDATED.value,
            {"updated_fields": list(update_data.keys())}
        )
    
    db.commit()
    db.refresh(application)
    return application


@router.patch("/{application_id}/stage", response_model=ApplicationSchema)
def update_application_stage(
    application_id: UUID,
    stage_data: ApplicationStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update application stage (for drag-and-drop)."""
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    old_stage = application.stage
    application.stage = stage_data.stage
    application.updated_at = datetime.utcnow()
    
    # Create timeline event
    create_timeline_event(
        db, application.id, TimelineEventType.STAGE_CHANGED.value,
        {"old_stage": old_stage.value, "new_stage": application.stage.value}
    )
    
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}")
def delete_application(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an application."""
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}
