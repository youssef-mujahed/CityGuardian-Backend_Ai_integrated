from app.database.postgres import init_postgres, close_postgres, get_db, create_tables

# Firebase - comment out for now
# from app.database.firebase import init_firebase, get_firestore, COLLECTION_ACTIVE_INCIDENTS, COLLECTION_VEHICLE_LOCATIONS, COLLECTION_LIVE_ALERTS, COLLECTION_TRAFFIC_CONDITIONS, COLLECTION_NOTIFICATIONS_QUEUE

__all__ = [
    "init_postgres",
    "close_postgres", 
    "get_db",
    "create_tables",
    # "init_firebase",
    # "get_firestore",
    # "COLLECTION_ACTIVE_INCIDENTS",
    # "COLLECTION_VEHICLE_LOCATIONS",
    # "COLLECTION_LIVE_ALERTS",
    # "COLLECTION_TRAFFIC_CONDITIONS",
    # "COLLECTION_NOTIFICATIONS_QUEUE",
]