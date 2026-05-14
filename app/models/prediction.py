from sqlalchemy import Column, DateTime, Integer, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database.base import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    severity_prediction = Column(Integer, nullable=False)
    factors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    was_accurate = Column(Boolean, nullable=True)