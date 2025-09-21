from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from uuid import UUID

from ...db.session import get_db
from ...models.user import User
from ...models.application import Application
from ...models.timeline_event import TimelineEvent
from ...schemas.timeline import TimelineEventList
from ...core.deps import get_current_user

router = APIRouter()


@router.get("/applications/{application_id}/timeline", response_model=TimelineEventList)
def get_application_timeline(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get timeline events for a specific application."""
    # Verify application ownership
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    events = db.query(TimelineEvent).filter(
        TimelineEvent.application_id == application_id
    ).order_by(desc(TimelineEvent.created_at)).all()
    
    return TimelineEventList(
        events=events,
        total=len(events)
    )
