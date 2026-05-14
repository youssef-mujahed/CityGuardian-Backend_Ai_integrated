from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database.postgres import get_db
from app.schemas.hospital import HospitalCreate, HospitalResponse, RouteRequest
from app.services.routing_service import RoutingService
from app.api.deps.auth_deps import require_admin, get_current_user
from app.models.user import User

router = APIRouter()

# ========== HOSPITAL ENDPOINTS ==========

@router.get("/hospitals", response_model=List[HospitalResponse])
def get_hospitals(
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all hospitals"""
    hospitals = RoutingService.get_all_hospitals(db, active_only)
    return hospitals

@router.post("/hospitals", response_model=HospitalResponse)
def add_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Add a new hospital (Admin only)"""
    try:
        hospital = RoutingService.add_hospital(db, hospital_data.dict())
        return hospital
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ========== ROUTING ENDPOINTS ==========

@router.post("/routes/to-hospital")
def get_route_to_hospital(
    incident_id: UUID,
    route_request: RouteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get best route from incident to nearest hospital"""
    try:
        result = RoutingService.get_best_route_to_hospital(
            db,
            incident_id,
            route_request.incident_latitude,
            route_request.incident_longitude
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes/eta")
def get_eta_for_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ETA for an existing incident (uses saved route)"""
    try:
        route = RoutingService.get_saved_route_for_incident(db, incident_id)
        return {
            "incident_id": incident_id,
            "eta_seconds": route.eta_seconds,
            "eta_minutes": round(route.eta_seconds / 60),
            "distance_meters": route.distance_meters,
            "distance_km": round(route.distance_meters / 1000, 1),
            "route_created_at": route.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))