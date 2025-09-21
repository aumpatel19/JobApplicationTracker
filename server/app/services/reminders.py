from datetime import date, datetime
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..db.session import SessionLocal
from ..models.user import User
from ..models.application import Application
from .email import email_service
import logging

logger = logging.getLogger(__name__)


def get_reminder_items_for_user(db: Session, user: User) -> List[Dict[str, Any]]:
    """Get reminder items for a user."""
    today = date.today()
    
    # Get applications with due actions (today or overdue)
    applications = db.query(Application).filter(
        Application.user_id == user.id,
        Application.next_action_due <= today,
        Application.next_action.isnot(None),
        Application.next_action != ""
    ).all()
    
    reminder_items = []
    for app in applications:
        is_overdue = app.next_action_due < today
        
        reminder_items.append({
            'id': str(app.id),
            'company': app.company,
            'role_title': app.role_title,
            'next_action': app.next_action,
            'next_action_due': app.next_action_due.strftime('%Y-%m-%d'),
            'is_overdue': is_overdue
        })
    
    return reminder_items


def send_daily_reminders():
    """Send daily reminder emails to all users."""
    logger.info("Starting daily reminder job")
    
    db = SessionLocal()
    try:
        # Get all users with email reminders enabled
        users = db.query(User).filter(User.email_reminders_enabled == True).all()
        
        sent_count = 0
        total_users = len(users)
        
        for user in users:
            try:
                # Get reminder items for this user
                reminder_items = get_reminder_items_for_user(db, user)
                
                if reminder_items:
                    # Send reminder email
                    success = email_service.send_daily_reminders(
                        user.email,
                        user.name,
                        reminder_items
                    )
                    
                    if success:
                        sent_count += 1
                        logger.info(f"Sent reminder to {user.email} with {len(reminder_items)} items")
                    else:
                        logger.error(f"Failed to send reminder to {user.email}")
                else:
                    logger.debug(f"No reminders for {user.email}")
                    
            except Exception as e:
                logger.error(f"Error processing reminders for {user.email}: {str(e)}")
        
        logger.info(f"Daily reminder job completed. Sent {sent_count}/{total_users} emails")
        
    except Exception as e:
        logger.error(f"Error in daily reminder job: {str(e)}")
    finally:
        db.close()
