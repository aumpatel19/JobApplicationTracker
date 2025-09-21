from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional

from ...db.session import get_db
from ...models.user import User
from ...models.application import Application, ApplicationStage, ApplicationPriority, ApplicationSource
from ...utils.csv_io import import_applications_from_csv, export_applications_to_csv
from ...core.deps import get_current_user

router = APIRouter()


@router.post("/import")
def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import applications from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        # Read CSV content
        content = file.file.read().decode('utf-8')
        
        # Import applications
        import_result = import_applications_from_csv(content, current_user.id)
        
        # Save successful applications to database
        for app_data in import_result["applications"]:
            application = Application(**app_data)
            db.add(application)
        
        db.commit()
        
        return {
            "message": "Import completed",
            "total_rows": import_result["total_rows"],
            "successful_imports": import_result["successful_imports"],
            "errors": import_result["errors"]
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.get("/export")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None,
    stage: Optional[ApplicationStage] = None,
    priority: Optional[ApplicationPriority] = None,
    source: Optional[ApplicationSource] = None,
):
    """Export applications to CSV with current filters."""
    query = db.query(Application).filter(Application.user_id == current_user.id)
    
    # Apply the same filters as the applications list
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
    
    applications = query.all()
    
    # Generate CSV content
    csv_content = export_applications_to_csv(applications)
    
    # Return as downloadable file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=job_applications.csv"}
    )
