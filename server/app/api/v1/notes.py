from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from uuid import UUID

from ...db.session import get_db
from ...models.user import User
from ...models.note import Note
from ...models.application import Application
from ...models.timeline_event import TimelineEvent, TimelineEventType
from ...schemas.note import NoteCreate, NoteUpdate, Note as NoteSchema, NoteList
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


@router.get("/applications/{application_id}/notes", response_model=NoteList)
def get_application_notes(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get notes for a specific application."""
    # Verify application ownership
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    query = db.query(Note).filter(
        and_(Note.application_id == application_id, Note.user_id == current_user.id)
    ).order_by(desc(Note.created_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    notes = query.offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return NoteList(
        notes=notes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/applications/{application_id}/notes", response_model=NoteSchema)
def create_note(
    application_id: UUID,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new note for an application."""
    # Verify application ownership
    application = db.query(Application).filter(
        and_(Application.id == application_id, Application.user_id == current_user.id)
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    note = Note(
        **note_data.model_dump(),
        application_id=application_id,
        user_id=current_user.id
    )
    db.add(note)
    db.flush()
    
    # Create timeline event
    create_timeline_event(
        db, application_id, TimelineEventType.NOTE_ADDED.value,
        {"note_preview": note.content[:100] + "..." if len(note.content) > 100 else note.content}
    )
    
    db.commit()
    db.refresh(note)
    return note


@router.get("/notes/{note_id}", response_model=NoteSchema)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific note."""
    note = db.query(Note).filter(
        and_(Note.id == note_id, Note.user_id == current_user.id)
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return note


@router.put("/notes/{note_id}", response_model=NoteSchema)
def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a note."""
    note = db.query(Note).filter(
        and_(Note.id == note_id, Note.user_id == current_user.id)
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields
    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}")
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a note."""
    note = db.query(Note).filter(
        and_(Note.id == note_id, Note.user_id == current_user.id)
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}
