from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from app.models.incident import Incident, IncidentType, IncidentStatus, IncidentSource
from app.models.incident_update import IncidentUpdate
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate as IncidentUpdateSchema

class IncidentService:
    
    @staticmethod
    def create_incident(
        db: Session,
        incident_data: IncidentCreate,
        user: User
    ) -> Incident:
        """Create a new incident report (Citizen or AI)"""
        
        new_incident = Incident(
            type=incident_data.type,
            severity=incident_data.severity,
            latitude=incident_data.location.latitude,
            longitude=incident_data.location.longitude,
            status=IncidentStatus.REPORTED,
            source=IncidentSource.CITIZEN_REPORT,
            reported_by=user.id,
            description=incident_data.description,
            ai_confidence=None
        )
        
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        
        # Create initial update log
        update_log = IncidentUpdate(
            incident_id=new_incident.id,
            status=IncidentStatus.REPORTED,
            note=f"Incident reported by {user.full_name}",
            updated_by=user.id
        )
        db.add(update_log)
        db.commit()
        
        return new_incident
    
    @staticmethod
    def get_incident_by_id(db: Session, incident_id: UUID) -> Incident:
        """Get single incident by ID"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise ValueError("Incident not found")
        return incident
    
    @staticmethod
    def get_all_incidents(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        incident_type: Optional[str] = None
    ) -> List[Incident]:
        """Get all incidents with filters (Admin only)"""
        
        query = db.query(Incident)
        
        if status:
            query = query.filter(Incident.status == status)
        
        if incident_type:
            query = query.filter(Incident.type == incident_type)
        
        return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_active_incidents(db: Session) -> List[Incident]:
        """Get all non-resolved incidents (for live dashboard)"""
        
        return db.query(Incident).filter(
            Incident.status != IncidentStatus.RESOLVED
        ).order_by(Incident.created_at.desc()).all()
    
    @staticmethod
    def get_my_incidents(db: Session, user_id: UUID) -> List[Incident]:
        """Get incidents reported by specific user (Citizen)"""
        
        return db.query(Incident).filter(
            Incident.reported_by == user_id
        ).order_by(Incident.created_at.desc()).all()
    
    @staticmethod
    def update_incident(
        db: Session,
        incident_id: UUID,
        update_data: IncidentUpdateSchema,
        user: User
    ) -> Incident:
        """Update incident status and details (Admin only)"""
        
        incident = IncidentService.get_incident_by_id(db, incident_id)
        
        old_status = incident.status
        
        if update_data.status:
            incident.status = update_data.status
        
        if update_data.severity:
            incident.severity = update_data.severity
        
        if update_data.description:
            incident.description = update_data.description
        
        if update_data.status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(incident)
        
        # Log the update
        if old_status != incident.status:
            update_log = IncidentUpdate(
                incident_id=incident.id,
                status=incident.status,
                note=f"Status changed from {old_status.value} to {incident.status.value} by {user.full_name}",
                updated_by=user.id
            )
            db.add(update_log)
            db.commit()
        
        return incident
    
    @staticmethod
    def get_incident_updates(db: Session, incident_id: UUID) -> List[IncidentUpdate]:
        """Get all updates for an incident"""
        
        return db.query(IncidentUpdate).filter(
            IncidentUpdate.incident_id == incident_id
        ).order_by(IncidentUpdate.created_at).all()