#!/usr/bin/env python
"""Create a test citizen user for mobile app"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.postgres import init_postgres, get_db
from app.services.auth_service import AuthService
from app.schemas.user import UserRegister
from app.models.user import UserRole

def main():
    print("Creating test citizen user for mobile app...")
    
    init_postgres()
    db = next(get_db())
    
    citizen_data = UserRegister(
        email="citizen@example.com",
        password="Citizen123!",
        full_name="Test Citizen",
        national_id="98765432109876",
        phone="01112345678",
        role=UserRole.CITIZEN
    )
    
    try:
        user = AuthService.register_user(db, citizen_data)
        print(f"✅ Citizen user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Password: Citizen123!")
        print(f"   Role: {user.role.value}")
        print(f"\nUse these credentials to login to mobile app")
    except ValueError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()