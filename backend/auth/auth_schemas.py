"""
Schemas adicionales para autenticación
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para crear un usuario"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema de respuesta de usuario"""
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema de token de acceso"""
    access_token: str
    token_type: str
    user: UserResponse


class LoginResponse(BaseModel):
    """Schema de respuesta de login"""
    success: bool
    message: str
    token: Optional[Token] = None