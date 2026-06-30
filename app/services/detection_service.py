import base64
import os
from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentType, IncidentStatus, IncidentSource

class DetectionService:
    
    @staticmethod
    def save_image(base64_string: str, incident_id: str) -> str:
        upload_dir = "uploads/incidents"
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{incident_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(upload_dir, filename)
        
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filepath
    
    @staticmethod
    def process_detection(db: Session, detection_data: dict) -> dict:
        
        if detection_data['confidence'] < 0.6:
            return {"status": "rejected", "reason": "Low confidence"}
        
        incident_id = uuid4()
        

        image_path = None
        if detection_data.get('image_base64'):
            try:
                image_path = DetectionService.save_image(
                    detection_data['image_base64'], 
                    str(incident_id)
                )
                print(f"✅ Image saved: {image_path}")
            except Exception as e:
                print(f"❌ Image error: {e}")
        
        # تسجيل الحادثة مع رابط الصورة
        new_incident = Incident(
            id=incident_id,
            type=IncidentType.ACCIDENT,
            severity=2,
            latitude=detection_data['latitude'],
            longitude=detection_data['longitude'],
            status=IncidentStatus.REPORTED,
            source=IncidentSource.AI_DETECTION,
            reported_by=None,
            ai_confidence=detection_data['confidence'],
            description=f"AI detected: {detection_data['class_name']}",
            image_url=image_path
        )
        
        db.add(new_incident)
        db.commit()
        
        print(f"✅ Incident {incident_id} saved")
        
        return {
            "incident_id": str(incident_id),
            "status": "reported",
            "severity_prediction": 2,
            "image_stored": image_path is not None
        }