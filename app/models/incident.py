from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.database.base import Base

class IncidentType(str, enum.Enum):
    ACCIDENT = "accident"
    FIRE = "fire"
    MEDICAL = "medical"

class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    VERIFIED = "verified"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"

class IncidentSource(str, enum.Enum):
    AI_DETECTION = "ai_detection"
    CITIZEN_REPORT = "citizen_report"
    MANUAL = "manual"

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.REPORTED)
    source = Column(Enum(IncidentSource), nullable=False)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)