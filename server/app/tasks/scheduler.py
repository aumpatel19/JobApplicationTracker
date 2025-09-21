from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from ..services.reminders import send_daily_reminders

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler():
    """Set up the background scheduler."""
    # Schedule daily reminders at 7:30 AM
    scheduler.add_job(
        send_daily_reminders,
        CronTrigger(hour=7, minute=30),  # 7:30 AM daily
        id='daily_reminders',
        name='Send daily reminder emails',
        replace_existing=True
    )
    
    logger.info("Scheduler configured with daily reminder job at 7:30 AM")


def start_scheduler():
    """Start the scheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
