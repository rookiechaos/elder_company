"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from services.logging_service import logger
from config.database import get_db
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.auth import get_current_user
from dependencies import get_auth_service_dependency
from schemas.auth import RegisterRequest, LoginRequest, DeviceRegisterRequest
from exceptions import ValidationError, ConflictError
import os

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register")
@rate_limit(limit=RATE_LIMITS["auth"])
async def register(
    http_request: Request,
    request: RegisterRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dependency)
):
    """Register a new user"""
    try:
        
        try:
            user_auth = auth_service.create_user(
                user_id=request.user_id,
                email=request.email,
                phone=request.phone,
                username=request.username,
                password=request.password,
                auth_method=request.auth_method
            )
        except ValueError as e:
            # User already exists or validation error
            db.rollback()  # Rollback the failed transaction
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg:
                raise ConflictError(f"User already exists: {str(e)}")
            raise ValidationError(f"Invalid registration data: {str(e)}")
        
        # Generate token
        token = auth_service.generate_token(request.user_id)
        
        logger.log_api_request(
            endpoint="/api/auth/register",
            method="POST",
            user_id=request.user_id,
            org_id=None,
            status_code=200,
            response_time_ms=0
        )
        
        return {
            "message": "User registered successfully",
            "user": user_auth,
            "token": token
        }
    except (ValidationError, ConflictError):
        raise
    except Exception as e:
        logger.log_error(e, {"action": "register"})
        raise


@router.post(
    "/login",
    summary="User login",
    description="Sign in with email, username, or phone; returns an auth token.",
    response_description="Auth token and user profile",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Authentication failed; invalid credentials"},
        500: {"description": "Internal server error"}
    }
)
@rate_limit(limit=RATE_LIMITS["auth"])
async def login(
    http_request: Request,
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login
    
    Sign in with identifier (email, username, or phone) and password.
    
    - **identifier**: User identifier (email, username, or phone)
    - **password**: Password
    
    Returns a JWT auth token for subsequent API requests.
    """
    try:
        auth_service = get_auth_service(db)
        
        user_auth = auth_service.authenticate(
            identifier=request.identifier,
            password=request.password
        )
        
        if not user_auth:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate token
        token = auth_service.generate_token(user_auth["user_id"])
        
        logger.log_api_request(
            endpoint="/api/auth/login",
            method="POST",
            user_id=user_auth["user_id"],
            org_id=None,
            status_code=200,
            response_time_ms=0
        )
        
        return {
            "message": "Login successful",
            "user": user_auth,
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "login"})
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/device/register")
async def register_device(
    request: DeviceRegisterRequest,
    current_user: dict = Depends(get_current_user),
    org_id: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service_dependency)
):
    """Register a device"""
    try:
        
        device_info = {
            "device_name": request.device_name,
            "device_type": request.device_type,
            "platform": request.platform,
            "device_model": request.device_model,
            "os_version": request.os_version,
            "app_version": request.app_version,
            "push_token": request.push_token
        }
        
        device = auth_service.register_device(
            user_id=current_user["user_id"],
            device_token=request.device_token,
            device_info=device_info,
            org_id=org_id
        )
        
        return {
            "message": "Device registered successfully",
            "device": device
        }
    except Exception as e:
        logger.log_error(e, {"action": "register_device"})
        raise HTTPException(status_code=500, detail=f"Device registration failed: {str(e)}")


@router.get("/devices")
async def get_devices(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service_dependency)
):
    """Get all devices for the user"""
    try:
        devices = auth_service.get_user_devices(current_user["user_id"])
        
        return {
            "devices": devices,
            "count": len(devices)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_devices"})
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service_dependency)
):
    """Get current user information"""
    try:
        from services.user_service import UserService
        
        user_service = UserService(db)
        profile = user_service.get_user_profile(current_user["user_id"])
        devices = auth_service.get_user_devices(current_user["user_id"])
        
        return {
            "user_id": current_user["user_id"],
            "profile": profile,
            "devices": devices
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_current_user_info"})
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")
