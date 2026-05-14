#!/usr/bin/env python
"""Create admin user for web dashboard"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.postgres import init_postgres, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from uuid import uuid4

def create_admin():
    """Create a single admin user"""
    
    print("=" * 50)
    print("Creating Admin User")
    print("=" * 50)
    
    # Admin credentials
    mobile = "01140307194"
    password = "abdallah123"
    full_name = "Abdallah Hisham"
    national_id = "11111111111111"
    
    # Initialize database
    init_postgres()
    db = next(get_db())
    
    # Check if mobile already exists
    existing = db.query(User).filter(User.mobile == mobile).first()
    if existing:
        print(f"⚠️ Admin with mobile {mobile} already exists!")
        print(f"   Login with: {mobile} / {password}")
        return
    
    # Hash password
    hashed_password = get_password_hash(password)
    
    # Create admin
    new_admin = User(
        id=uuid4(),
        mobile=mobile,
        password_hash=hashed_password,
        full_name=full_name,
        national_id=national_id,
        role=UserRole.ADMIN,
        email=None,
        is_active=True
    )
    
    db.add(new_admin)
    db.commit()
    
    print("\n✅ Admin user created successfully!")
    print("-" * 30)
    print(f"   Mobile: {mobile}")
    print(f"   Password: {password}")
    print(f"   Name: {full_name}")
    print("-" * 30)

if __name__ == "__main__":
    create_admin()