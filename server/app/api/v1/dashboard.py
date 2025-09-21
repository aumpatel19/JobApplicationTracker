from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
from typing import List

from ...db.session import get_db
from ...models.user import User
from ...models.application import Application, ApplicationStage
from ...models.timeline_event import TimelineEvent, TimelineEventType
from ...schemas.dashboard import DashboardData, KPICard, WeeklySubmission, StageFunnelData
from ...core.deps import get_current_user

router = APIRouter()


@router.get("/kpis", response_model=KPICard)
def get_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get KPI data for dashboard."""
    base_query = db.query(Application).filter(Application.user_id == current_user.id)
    
    total_applications = base_query.count()
    
    # Active applications (not rejected)
    active_applications = base_query.filter(
        Application.stage != ApplicationStage.REJECTED
    ).count()
    
    offers = base_query.filter(Application.stage == ApplicationStage.OFFER).count()
    rejections = base_query.filter(Application.stage == ApplicationStage.REJECTED).count()
    
    return KPICard(
        total_applications=total_applications,
        active_applications=active_applications,
        offers=offers,
        rejections=rejections
    )


@router.get("/weekly-submissions", response_model=List[WeeklySubmission])
def get_weekly_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly submission data for the last 6 weeks."""
    # Calculate the start date (6 weeks ago, start of week)
    today = date.today()
    days_since_monday = today.weekday()
    current_week_start = today - timedelta(days=days_since_monday)
    start_date = current_week_start - timedelta(weeks=5)
    
    # Query applications created in the last 6 weeks
    applications = db.query(Application).filter(
        and_(
            Application.user_id == current_user.id,
            Application.created_at >= start_date
        )
    ).all()
    
    # Group by week
    weekly_data = {}
    for week in range(6):
        week_start = start_date + timedelta(weeks=week)
        weekly_data[week_start] = 0
    
    for app in applications:
        app_date = app.created_at.date()
        days_since_monday = app_date.weekday()
        week_start = app_date - timedelta(days=days_since_monday)
        
        if week_start in weekly_data:
            weekly_data[week_start] += 1
    
    return [
        WeeklySubmission(week_start=week_start, count=count)
        for week_start, count in sorted(weekly_data.items())
    ]


@router.get("/stage-funnel", response_model=List[StageFunnelData])
def get_stage_funnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stage funnel data."""
    stage_counts = db.query(
        Application.stage,
        func.count(Application.id).label('count')
    ).filter(
        Application.user_id == current_user.id
    ).group_by(Application.stage).all()
    
    # Ensure all stages are represented
    all_stages = [stage.value for stage in ApplicationStage]
    stage_dict = {stage.stage.value: stage.count for stage in stage_counts}
    
    return [
        StageFunnelData(stage=stage, count=stage_dict.get(stage, 0))
        for stage in all_stages
    ]


@router.get("", response_model=DashboardData)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all dashboard data."""
    kpis = get_kpis(db, current_user)
    weekly_submissions = get_weekly_submissions(db, current_user)
    stage_funnel = get_stage_funnel(db, current_user)
    
    # Get recent activity (last 10 timeline events)
    recent_events = db.query(TimelineEvent).join(Application).filter(
        Application.user_id == current_user.id
    ).order_by(TimelineEvent.created_at.desc()).limit(10).all()
    
    recent_activity = []
    for event in recent_events:
        activity = {
            "id": str(event.id),
            "type": event.type,
            "created_at": event.created_at.isoformat(),
            "application_id": str(event.application_id),
            "payload": event.payload
        }
        recent_activity.append(activity)
    
    return DashboardData(
        kpis=kpis,
        weekly_submissions=weekly_submissions,
        stage_funnel=stage_funnel,
        recent_activity=recent_activity
    )
