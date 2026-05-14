from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.database.postgres import get_db
from app.services.ml_service import MLService
from app.api.deps.auth_deps import get_current_user, require_admin
from app.models.user import User
from app.models.risk_zone import RiskZone, RiskLevel
from uuid import uuid4

router = APIRouter()

# ========== REQUEST/RESPONSE MODELS ==========

class RiskPredictionRequest(BaseModel):
    latitude: float = Field(..., description="Latitude of location")
    longitude: float = Field(..., description="Longitude of location")
    hour: Optional[int] = Field(None, ge=0, le=23, description="Hour of day (0-23)")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Monday)")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month (1-12)")
    weather: str = Field("clear", description="Weather condition")
    traffic_density: str = Field("medium", description="Traffic density: low, medium, high")
    road_type: str = Field("urban", description="Road type: highway, intersection, urban, residential, rural")
    speed_limit: int = Field(60, ge=20, le=140, description="Speed limit in km/h")
    estimated_vehicles: int = Field(2, ge=1, le=10, description="Estimated number of vehicles involved")

class RiskPredictionResponse(BaseModel):
    location: dict
    risk_score: float
    risk_level: str
    is_high_risk: bool
    factors: dict
    base_severity: dict

class SeverityPredictionRequest(BaseModel):
    latitude: float
    longitude: float
    speed_limit: int = 60
    estimated_vehicles: int = 2
    weather: str = "clear"
    road_type: str = "highway"
    traffic_density: str = "medium"
    time_of_day: Optional[str] = None

class SeverityPredictionResponse(BaseModel):
    predicted_severity: int
    confidence: float
    severity_level: str
    recommended_response: str
    model_used: str

class RiskZoneCreate(BaseModel):
    latitude: float
    longitude: float
    radius_meters: int = 100
    risk_score: float
    risk_level: str
    accident_count: int = 0

# ========== PUBLIC ENDPOINTS (Logged-in Users) ==========

@router.post("/predict", response_model=RiskPredictionResponse)
def predict_risk(
    request: RiskPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict risk score for a location.
    
    Use this to:
    - Check if an area is high-risk
    - Get factors contributing to risk
    - Plan preventive measures
    """
    
    # Auto-fill time if not provided
    now = datetime.now()
    if request.hour is None:
        request.hour = now.hour
    if request.day_of_week is None:
        request.day_of_week = now.weekday()
    if request.month is None:
        request.month = now.month
    
    # Auto-fill time of day for severity
    if request.hour < 6:
        time_of_day = "dawn"
    elif request.hour < 18:
        time_of_day = "day"
    else:
        time_of_day = "night"
    
    # Prepare data for prediction
    data = request.dict()
    data["time_of_day"] = time_of_day
    
    # Get predictions
    result = MLService.predict_risk(data)
    
    return {
        "location": {
            "lat": request.latitude,
            "lng": request.longitude
        },
        **result
    }

@router.post("/severity", response_model=SeverityPredictionResponse)
def predict_severity(
    request: SeverityPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict accident severity for a location.
    
    Helps emergency services prepare appropriate response:
    - Severity 1 (MINOR): Standard ambulance
    - Severity 2 (MODERATE): Priority response with paramedics
    - Severity 3 (SEVERE): Critical response, trauma team
    """
    
    # Auto-fill time of day
    if request.time_of_day is None:
        hour = datetime.now().hour
        if hour < 6:
            request.time_of_day = "dawn"
        elif hour < 18:
            request.time_of_day = "day"
        else:
            request.time_of_day = "night"
    
    data = request.dict()
    result = MLService.predict_severity(data)
    
    return result

# ========== ADMIN ONLY ENDPOINTS ==========

@router.get("/zones")
def get_risk_zones(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all saved risk zones for heatmap (Admin only)"""
    
    zones = db.query(RiskZone).order_by(RiskZone.risk_score.desc()).all()
    
    return [
        {
            "id": str(z.id),
            "latitude": z.latitude,
            "longitude": z.longitude,
            "radius_meters": z.radius_meters,
            "risk_score": z.risk_score,
            "risk_level": z.risk_level.value,
            "accident_count": z.accident_count_6months,
            "last_calculated": z.last_calculated.isoformat() if z.last_calculated else None
        }
        for z in zones
    ]

@router.post("/zones")
def create_risk_zone(
    zone_data: RiskZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Save a risk zone to database (Admin only)"""
    
    # Convert string risk level to enum
    risk_level_enum = RiskLevel.LOW
    if zone_data.risk_level.upper() == "MEDIUM":
        risk_level_enum = RiskLevel.MEDIUM
    elif zone_data.risk_level.upper() == "HIGH":
        risk_level_enum = RiskLevel.HIGH
    
    new_zone = RiskZone(
        id=uuid4(),
        latitude=zone_data.latitude,
        longitude=zone_data.longitude,
        radius_meters=zone_data.radius_meters,
        risk_score=zone_data.risk_score,
        risk_level=risk_level_enum,
        accident_count_6months=zone_data.accident_count
    )
    
    db.add(new_zone)
    db.commit()
    db.refresh(new_zone)
    
    return {
        "message": "Risk zone created successfully",
        "id": str(new_zone.id)
    }

@router.delete("/zones/{zone_id}")
def delete_risk_zone(
    zone_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a risk zone (Admin only)"""
    
    from uuid import UUID
    zone = db.query(RiskZone).filter(RiskZone.id == UUID(zone_id)).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Risk zone not found")
    
    db.delete(zone)
    db.commit()
    
    return {"message": "Risk zone deleted successfully"}

@router.get("/heatmap")
def get_heatmap_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get GeoJSON data for risk heatmap visualization (Admin only)"""
    
    zones = db.query(RiskZone).all()
    
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [z.longitude, z.latitude]
                },
                "properties": {
                    "risk_score": z.risk_score,
                    "risk_level": z.risk_level.value,
                    "accident_count": z.accident_count_6months,
                    "radius": z.radius_meters,
                    "zone_id": str(z.id)
                }
            }
            for z in zones
        ]
    }

@router.get("/health")
def health_check():
    """Check if ML models are loaded"""
    return {
        "model_loaded": MLService._severity_model is not None,
        "pipeline_loaded": MLService._pipeline is not None,
        "status": "ready" if MLService._severity_model else "degraded"
    }