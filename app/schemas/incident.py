from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum
from app.schemas.common import Location

class IncidentType(str, Enum):
    ACCIDENT = "accident"
    FIRE = "fire"
    MEDICAL = "medical"

class IncidentStatus(str, Enum):
    REPORTED = "reported"
    VERIFIED = "verified"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"

class IncidentSource(str, Enum):
    AI_DETECTION = "ai_detection"
    CITIZEN_REPORT = "citizen_report"
    MANUAL = "manual"

class IncidentCreate(BaseModel):
    type: IncidentType
    location: Location
    description: Optional[str] = None
    severity: int = Field(..., ge=1, le=3)

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    severity: Optional[int] = Field(None, ge=1, le=3)
    description: Optional[str] = None

from typing import Optional

class IncidentResponse(BaseModel):
    id: UUID
    type: IncidentType
    severity: int
    latitude: float
    longitude: float
    status: IncidentStatus
    source: IncidentSource
    reported_by: Optional[UUID] = None  # <-- أضف Optional
    verified_by: Optional[UUID] = None  # <-- أضف Optional لو موجود
    ai_confidence: Optional[float] = None
    description: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    image_url: Optional[str] = None  # <-- أضف لو مش موجود