"""
API request/response schemas - Pydantic models for routes.
"""

from schemas.auth import RegisterRequest, LoginRequest, DeviceRegisterRequest

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "DeviceRegisterRequest",
]
