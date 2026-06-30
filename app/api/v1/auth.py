from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.postgres import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token, RegisterWithPhoneRequest
from app.services.auth_service import AuthService
from app.api.deps.auth_deps import get_current_user, require_admin, require_citizen
from app.models.user import User, UserRole
from app.core.firebase_auth import verify_firebase_token
from app.core.security import get_password_hash, create_access_token
from uuid import UUID

router = APIRouter()



@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        user = AuthService.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        result = AuthService.login_user(db, user_data.mobile, user_data.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_admin)):
    return {
        "message": "Welcome to admin dashboard",
        "user": current_user.full_name,
        "role": current_user.role.value
    }

@router.get("/citizen/profile")
def citizen_profile(current_user: User = Depends(require_citizen)):
    return current_user




@router.post("/register-with-phone", response_model=Token)
def register_with_phone(
    request: RegisterWithPhoneRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user after Firebase phone verification.
    Mobile app sends Firebase ID token after successful OTP verification.
    """
    
    
    firebase_user = verify_firebase_token(request.firebase_id_token)
    if not firebase_user:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase token")
    

    firebase_uid = firebase_user.get('uid')
    phone_number = firebase_user.get('phone_number')
    
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number not verified in Firebase")
    
    
    existing_user = db.query(User).filter(User.mobile == phone_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    existing_firebase = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if existing_firebase:
        raise HTTPException(status_code=400, detail="Firebase account already linked")
    
    
    hashed_password = get_password_hash(request.password)
    

    new_user = User(
        mobile=phone_number,
        password_hash=hashed_password,
        full_name=request.full_name,
        national_id=request.national_id,
        firebase_uid=firebase_uid,
        role=UserRole.CITIZEN
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),
            "mobile": new_user.mobile,
            "role": new_user.role.value
        }
    )
    
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "mobile": new_user.mobile,
            "full_name": new_user.full_name,
            "national_id": new_user.national_id,
            "role": new_user.role.value,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        }
    }