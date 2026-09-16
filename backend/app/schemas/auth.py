from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.models.user import UserRole

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int # seconds
    refresh_token: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.FRAUD_ANALYST
    organization_name: Optional[str] = "Default Organization"
