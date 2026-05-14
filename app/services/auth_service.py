from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.user import UserRegister
from app.core.security import verify_password, get_password_hash, create_access_token
from uuid import UUID
from datetime import datetime

class AuthService:
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Register a new user with mobile + national ID + password only"""
        
        # Check if mobile exists
        existing_mobile = db.query(User).filter(User.mobile == user_data.mobile).first()
        if existing_mobile:
            raise ValueError("Mobile number already registered")
        
        # Check if national_id exists
        existing_national = db.query(User).filter(User.national_id == user_data.national_id).first()
        if existing_national:
            raise ValueError("National ID already registered")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Use Flutter's full_name if provided, otherwise auto-generate
        if user_data.full_name and user_data.full_name.strip():
            full_name = user_data.full_name.strip()
        else:
            full_name = f"User_{user_data.mobile[-4:]}"
        
        # Create user
        new_user = User(
            mobile=user_data.mobile,
            password_hash=hashed_password,
            full_name=full_name,  # Now uses Flutter's value if provided
            national_id=user_data.national_id,
            role=UserRole.CITIZEN,  # Default role
            email=None
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def login_user(db: Session, mobile: str, password: str) -> dict:
        """Login with mobile number and password"""
        
        # Clean mobile number
        mobile_clean = ''.join(filter(str.isdigit, mobile))
        
        # Find user by mobile
        user = db.query(User).filter(User.mobile == mobile_clean).first()
        if not user:
            raise ValueError("Invalid mobile number or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid mobile number or password")
        
        # Check if active
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create token
        token_data = {
            "sub": str(user.id),
            "mobile": user.mobile,
            "role": user.role.value
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "mobile": user.mobile,
                "full_name": user.full_name,
                "national_id": user.national_id,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user