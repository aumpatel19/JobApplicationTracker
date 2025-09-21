import csv
import io
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID

from ..models.application import Application, ApplicationStage, ApplicationPriority, ApplicationSource, EmploymentType


def parse_date(date_str: str) -> Optional[date]:
    """Parse date string in various formats."""
    if not date_str or date_str.strip() == "":
        return None
    
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def parse_enum(value: str, enum_class, default=None):
    """Parse enum value safely."""
    if not value or value.strip() == "":
        return default
    
    # Try exact match first
    for enum_val in enum_class:
        if enum_val.value.lower() == value.strip().lower():
            return enum_val
    
    # If no exact match, return default
    return default


def validate_csv_row(row: Dict[str, str], row_num: int) -> Dict[str, Any]:
    """Validate and convert a CSV row to application data."""
    errors = []
    data = {}
    
    # Required fields
    if not row.get("role_title", "").strip():
        errors.append(f"Row {row_num}: role_title is required")
    else:
        data["role_title"] = row["role_title"].strip()
    
    if not row.get("company", "").strip():
        errors.append(f"Row {row_num}: company is required")
    else:
        data["company"] = row["company"].strip()
    
    # Optional fields
    data["location"] = row.get("location", "").strip() or None
    data["salary_range"] = row.get("salary_range", "").strip() or None
    data["next_action"] = row.get("next_action", "").strip() or None
    
    # Enum fields
    try:
        data["stage"] = parse_enum(
            row.get("stage", ""), ApplicationStage, ApplicationStage.DRAFT
        )
    except Exception as e:
        errors.append(f"Row {row_num}: Invalid stage value")
        data["stage"] = ApplicationStage.DRAFT
    
    try:
        data["priority"] = parse_enum(
            row.get("priority", ""), ApplicationPriority, ApplicationPriority.MEDIUM
        )
    except Exception as e:
        errors.append(f"Row {row_num}: Invalid priority value")
        data["priority"] = ApplicationPriority.MEDIUM
    
    try:
        data["source"] = parse_enum(
            row.get("source", ""), ApplicationSource, ApplicationSource.OTHER
        )
    except Exception as e:
        errors.append(f"Row {row_num}: Invalid source value")
        data["source"] = ApplicationSource.OTHER
    
    try:
        data["employment_type"] = parse_enum(
            row.get("employment_type", ""), EmploymentType, None
        )
    except Exception as e:
        errors.append(f"Row {row_num}: Invalid employment_type value")
    
    # Date fields
    try:
        if row.get("next_action_due"):
            data["next_action_due"] = parse_date(row["next_action_due"])
        else:
            data["next_action_due"] = None
    except ValueError as e:
        errors.append(f"Row {row_num}: Invalid next_action_due date format")
        data["next_action_due"] = None
    
    return {"data": data, "errors": errors}


def import_applications_from_csv(
    csv_content: str, user_id: UUID
) -> Dict[str, Any]:
    """Import applications from CSV content."""
    reader = csv.DictReader(io.StringIO(csv_content))
    
    results = {
        "total_rows": 0,
        "successful_imports": 0,
        "errors": [],
        "applications": []
    }
    
    for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
        results["total_rows"] += 1
        
        validation_result = validate_csv_row(row, row_num)
        
        if validation_result["errors"]:
            results["errors"].extend(validation_result["errors"])
            continue
        
        # Create application data
        app_data = validation_result["data"]
        app_data["user_id"] = user_id
        
        results["applications"].append(app_data)
        results["successful_imports"] += 1
    
    return results


def export_applications_to_csv(applications: List[Application]) -> str:
    """Export applications to CSV format."""
    output = io.StringIO()
    
    fieldnames = [
        "role_title", "company", "location", "employment_type", "salary_range",
        "source", "stage", "priority", "next_action", "next_action_due",
        "created_at", "updated_at"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for app in applications:
        row = {
            "role_title": app.role_title,
            "company": app.company,
            "location": app.location or "",
            "employment_type": app.employment_type.value if app.employment_type else "",
            "salary_range": app.salary_range or "",
            "source": app.source.value,
            "stage": app.stage.value,
            "priority": app.priority.value,
            "next_action": app.next_action or "",
            "next_action_due": app.next_action_due.isoformat() if app.next_action_due else "",
            "created_at": app.created_at.isoformat(),
            "updated_at": app.updated_at.isoformat()
        }
        writer.writerow(row)
    
    return output.getvalue()
