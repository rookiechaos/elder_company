"""
Auth API request/response schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    """Register a new user request"""
    user_id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    auth_method: str = "password"


class LoginRequest(BaseModel):
    """User login request"""
    identifier: str  # email, phone, or username
    password: str


class DeviceRegisterRequest(BaseModel):
    """Device registration request"""
    device_token: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None  # mobile, tablet, web
    platform: Optional[str] = None  # ios, android, web
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_token: Optional[str] = None
