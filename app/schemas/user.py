from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "admin"
    CITIZEN = "citizen"

class UserRegister(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=15)
    national_id: str = Field(..., min_length=14, max_length=14)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None)  # ← This must exist
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v):
        v = ''.join(filter(str.isdigit, v))
        if len(v) < 10:
            raise ValueError('Mobile number must be at least 10 digits')
        if not v.startswith('01'):
            raise ValueError('Mobile number must start with 01')
        return v
    
    @field_validator('national_id')
    @classmethod
    def validate_national_id(cls, v):
        if not v.isdigit():
            raise ValueError('National ID must contain only numbers')
        if len(v) != 14:
            raise ValueError('National ID must be exactly 14 digits')
        return v

class UserLogin(BaseModel):
    mobile: str = Field(..., description="Mobile number")
    password: str

class UserResponse(BaseModel):
    id: UUID
    mobile: str
    full_name: Optional[str] = None
    national_id: str
    role: UserRole
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
class RegisterWithPhoneRequest(BaseModel):
    firebase_id_token: str
    national_id: str
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)