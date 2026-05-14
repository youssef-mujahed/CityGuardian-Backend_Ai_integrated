import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings

_firestore_client = None
_initialized = False

# Collection names - use these constants everywhere
COLLECTION_ACTIVE_INCIDENTS = "active_incidents"
COLLECTION_VEHICLE_LOCATIONS = "vehicle_locations"
COLLECTION_LIVE_ALERTS = "live_alerts"
COLLECTION_TRAFFIC_CONDITIONS = "traffic_conditions"
COLLECTION_NOTIFICATIONS_QUEUE = "notifications_queue"

def init_firebase():
    """Initialize Firebase - call this on startup"""
    global _firestore_client, _initialized
    
    if _initialized:
        return
    
    try:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        _initialized = True
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        _firestore_client = None

def get_firestore():
    """Get Firestore client - use as FastAPI dependency"""
    if not _initialized:
        init_firebase()
    return _firestore_client