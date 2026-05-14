#!/usr/bin/env python
"""Initialize database tables - Run with: python scripts/init_db.py"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.postgres import init_postgres, create_tables, close_postgres

def main():
    print("Initializing database...")
    
    # Initialize connection first
    init_postgres()
    
    # IMPORTANT: Import only the models you want
    from app.models import (
        User,
        Incident, 
        IncidentUpdate,
        Hospital,
        Route,
        RiskZone,
        Prediction,
        # Notification,  # Removed for now
        # ApiLog,       # Removed for now
    )
    
    # Now create tables (models are now registered)
    create_tables()
    
    print("✅ Database tables created successfully!")
    close_postgres()

if __name__ == "__main__":
    main()