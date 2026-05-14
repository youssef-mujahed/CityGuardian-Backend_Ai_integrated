from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database.postgres import get_db
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate
from app.services.incident_service import IncidentService
from app.api.deps.auth_deps import get_current_user, require_admin, require_citizen
from app.models.user import User

router = APIRouter()

# ========== CITIZEN ENDPOINTS ==========

@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen)
):
    """
    Report a new incident (Citizen only)
    
    - Type: accident, fire, or medical
    - Severity: 1 (minor), 2 (moderate), or 3 (severe)
    - Location: latitude and longitude
    """
    try:
        incident = IncidentService.create_incident(db, incident_data, current_user)
        return incident
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my", response_model=List[IncidentResponse])
def get_my_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_citizen)
):
    """Get incidents reported by me (Citizen only)"""
    incidents = IncidentService.get_my_incidents(db, current_user.id)
    return incidents

# ========== ADMIN ENDPOINTS ==========

@router.get("/", response_model=List[IncidentResponse])
def get_all_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Filter by status: reported, verified, dispatched, resolved"),
    incident_type: Optional[str] = Query(None, description="Filter by type: accident, fire, medical"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all incidents with filters (Admin only)
    """
    incidents = IncidentService.get_all_incidents(db, skip, limit, status, incident_type)
    return incidents

@router.get("/active", response_model=List[IncidentResponse])
def get_active_incidents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all active (non-resolved) incidents for live dashboard (Admin only)
    """
    incidents = IncidentService.get_active_incidents(db)
    return incidents

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get incident details by ID (Admin only)
    """
    try:
        incident = IncidentService.get_incident_by_id(db, incident_id)
        return incident
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: UUID,
    update_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update incident status or details (Admin only)
    """
    try:
        incident = IncidentService.update_incident(db, incident_id, update_data, current_user)
        return incident
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{incident_id}/updates")
def get_incident_updates(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all status updates for an incident (Admin only)"""
    try:
        updates = IncidentService.get_incident_updates(db, incident_id)
        return updates
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))