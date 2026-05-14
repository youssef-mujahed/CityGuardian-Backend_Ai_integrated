from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class HospitalCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    phone: Optional[str] = None
    capacity: int = 50

class HospitalResponse(BaseModel):
    id: UUID
    name: str
    latitude: float
    longitude: float
    address: Optional[str]
    phone: Optional[str]
    capacity: int
    is_active: bool
    created_at: datetime

class RouteRequest(BaseModel):
    incident_latitude: float
    incident_longitude: float