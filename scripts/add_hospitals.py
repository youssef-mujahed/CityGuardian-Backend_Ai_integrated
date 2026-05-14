#!/usr/bin/env python
"""Add sample hospitals to database"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.postgres import init_postgres, get_db
from app.services.routing_service import RoutingService

# Sample hospitals in Cairo
hospitals = [
    {
        "name": "Cairo University Hospital",
        "latitude": 30.0272,
        "longitude": 31.2106,
        "address": "1 Giza St, Oula, Giza",
        "phone": "0223645678",
        "capacity": 500
    },
    {
        "name": "Al Demerdash Hospital",
        "latitude": 30.0636,
        "longitude": 31.2759,
        "address": "Demerdash, Abdeen, Cairo",
        "phone": "0225786554",
        "capacity": 400
    },
    {
        "name": "Maadi Military Hospital",
        "latitude": 29.9692,
        "longitude": 31.2583,
        "address": "Maadi, Cairo",
        "phone": "0225200333",
        "capacity": 300
    },
    {
        "name": "Heliopolis Hospital",
        "latitude": 30.0904,
        "longitude": 31.3274,
        "address": "Heliopolis, Cairo",
        "phone": "0224144444",
        "capacity": 250
    }
]

def main():
    print("Adding hospitals...")
    
    init_postgres()
    db = next(get_db())
    
    for h in hospitals:
        try:
            hospital = RoutingService.add_hospital(db, h)
            print(f"✅ Added: {hospital.name}")
        except Exception as e:
            print(f"❌ Error adding {h['name']}: {e}")

if __name__ == "__main__":
    main()