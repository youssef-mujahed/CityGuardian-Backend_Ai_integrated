from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres import get_db
from app.schemas.detection import DetectionRequest, DetectionResponse
from app.services.detection_service import DetectionService
import os
from fastapi.responses import FileResponse
from uuid import UUID
from app.models.incident import Incident

router = APIRouter()

@router.post("/detect/accident", response_model=DetectionResponse)
def detect_accident(
    detection: DetectionRequest,
    db: Session = Depends(get_db)
):
    result = DetectionService.process_detection(db, detection.dict())
    
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("reason"))
    
    return DetectionResponse(
        incident_id=result["incident_id"],
        status=result["status"],
        severity_prediction=result["severity_prediction"],
        image_stored=result["image_stored"]
    )



@router.get("/image/{incident_id}")
def get_incident_image(
    incident_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get accident image by incident ID.
    Use this in dashboard: <img src="/api/v1/detection/image/{incident_id}" />
    """
    try:
        incident = db.query(Incident).filter(Incident.id == UUID(incident_id)).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        if not incident.image_url:
            raise HTTPException(status_code=404, detail="Image not found for this incident")
        
        if os.path.exists(incident.image_url):
            return FileResponse(incident.image_url)
        else:
            raise HTTPException(status_code=404, detail="Image file not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid incident ID format")