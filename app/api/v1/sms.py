from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.sms_service import SMSService
from app.api.deps.auth_deps import require_admin
from app.models.user import User

router = APIRouter()

# ========== REQUEST MODELS ==========

class SendSMSRequest(BaseModel):
    phone_number: str = Field(
        ..., 
        min_length=10, 
        max_length=15,
        description="Recipient phone number (e.g., 01288163064)"
    )
    message: str = Field(
        ...,
        max_length=160,
        description="SMS content (max 160 characters)"
    )

class EmergencyAlertRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient phone number")
    incident_type: str = Field(..., description="accident, fire, or medical")
    location: str = Field(..., description="Description of the location")
    severity: int = Field(..., ge=1, le=3, description="1=minor, 2=moderate, 3=severe")
    incident_id: Optional[str] = None



@router.post("/send")
def send_sms(
    request: SendSMSRequest,
    current_user: User = Depends(require_admin)
):
    """Send SMS to Egyptian number (Admin only)"""
    
    result = SMSService.send_sms(
        phone_number=request.phone_number,
        message=request.message
    )
    
    if result:
        return {
            "success": True,
            "message": "SMS sent successfully",
            "to": request.phone_number
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to send SMS")

@router.post("/emergency")
def send_emergency_alert(
    request: EmergencyAlertRequest,
    current_user: User = Depends(require_admin)
):
    """Send formatted emergency alert (Admin only)"""
    
    result = SMSService.send_emergency_alert(
        phone_number=request.phone_number,
        incident_type=request.incident_type,
        location=request.location,
        severity=request.severity,
        incident_id=request.incident_id
    )
    
    if result:
        return {
            "success": True, 
            "message": "Emergency alert sent",
            "to": request.phone_number
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to send alert")

@router.get("/health")
def sms_health_check(current_user: User = Depends(require_admin)):
    """Check SMS service status (Admin only)"""
    
    try:
        SMSService.test_connection()
        return {
            "status": "healthy", 
            "message": "SMS service ready",
            "carrier": "MoceanAPI"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": f"SMS service error: {e}"
        }