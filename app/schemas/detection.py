from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DetectionRequest(BaseModel):
    timestamp: str
    class_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    image_base64: str

class DetectionResponse(BaseModel):
    incident_id: str
    status: str
    severity_prediction: int
    image_stored: bool