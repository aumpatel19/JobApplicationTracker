from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from uuid import UUID
from typing import Optional

from ...db.session import get_db
from ...models.user import User
from ...models.contact import Contact
from ...models.application import Application
from ...models.timeline_event import TimelineEvent, TimelineEventType
from ...schemas.contact import ContactCreate, ContactUpdate, Contact as ContactSchema, ContactList
from ...core.deps import get_current_user

router = APIRouter()


def create_timeline_event(db: Session, application_id: UUID, event_type: str, payload: dict = None):
    """Create a timeline event for an application."""
    if application_id:
        event = TimelineEvent(
            application_id=application_id,
            type=event_type,
            payload=payload or {}
        )
        db.add(event)


@router.get("", response_model=ContactList)
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    application_id: Optional[UUID] = Query(None, description="Filter by application"),
    search: Optional[str] = Query(None, description="Search in name, role, email"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get user's contacts with filtering and pagination."""
    query = db.query(Contact).filter(Contact.user_id == current_user.id)
    
    # Apply filters
    if application_id:
        query = query.filter(Contact.application_id == application_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Contact.name.ilike(search_term),
                Contact.role.ilike(search_term),
                Contact.email.ilike(search_term)
            )
        )
    
    # Apply sorting
    query = query.order_by(desc(Contact.created_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    contacts = query.offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return ContactList(
        contacts=contacts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=ContactSchema)
def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contact."""
    # Verify application ownership if application_id is provided
    if contact_data.application_id:
        application = db.query(Application).filter(
            and_(
                Application.id == contact_data.application_id,
                Application.user_id == current_user.id
            )
        ).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
    
    contact = Contact(**contact_data.model_dump(), user_id=current_user.id)
    db.add(contact)
    db.flush()
    
    # Create timeline event if linked to application
    if contact.application_id:
        create_timeline_event(
            db, contact.application_id, TimelineEventType.CONTACT_ADDED.value,
            {"contact_name": contact.name, "contact_role": contact.role}
        )
    
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactSchema)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contact."""
    contact = db.query(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == current_user.id)
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    return contact


@router.put("/{contact_id}", response_model=ContactSchema)
def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contact."""
    contact = db.query(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == current_user.id)
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Verify application ownership if application_id is being changed
    update_data = contact_data.model_dump(exclude_unset=True)
    if "application_id" in update_data and update_data["application_id"]:
        application = db.query(Application).filter(
            and_(
                Application.id == update_data["application_id"],
                Application.user_id == current_user.id
            )
        ).first()
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contact."""
    contact = db.query(Contact).filter(
        and_(Contact.id == contact_id, Contact.user_id == current_user.id)
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted successfully"}
