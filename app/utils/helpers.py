from datetime import datetime
from typing import Dict, Any
import json

def format_incident_for_firestore(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format incident data for Firestore storage"""
    return {
        "id": str(incident_data.get("id")),
        "type": incident_data.get("type"),
        "latitude": incident_data.get("latitude"),
        "longitude": incident_data.get("longitude"),
        "severity": incident_data.get("severity"),
        "status": incident_data.get("status"),
        "timestamp": datetime.utcnow().isoformat()
    }

def serialize_datetime(obj):
    """Helper to serialize datetime objects to JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def to_json(data):
    """Convert data to JSON with datetime handling"""
    return json.dumps(data, default=serialize_datetime)