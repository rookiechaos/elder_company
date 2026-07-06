"""
Night Mode API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from dependencies import require_auth, get_night_mode_service_dependency
from services.night_mode_service import NightModeService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors

router = APIRouter(prefix="/api/night-mode", tags=["night-mode"])


class UpdateNightModeConfigRequest(BaseModel):
    """Update night mode config request"""
    user_id: str = Field(..., min_length=1)
    user_type: str = Field(..., description="User type: elder, caregiver")
    enabled: Optional[bool] = None
    brightness: Optional[str] = Field(None, description="Brightness: low, medium, high")
    sound_enabled: Optional[bool] = None
    text_prompts: Optional[bool] = None
    start_time: Optional[str] = Field(None, description="Start time (HH:MM format)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM format)")
    sound_type: Optional[str] = Field(None, description="Sound type: gentle, calm, silent")
    volume: Optional[int] = Field(None, ge=0, le=100, description="Volume (0-100)")
    font_size: Optional[str] = Field(None, description="Font size: small, medium, large, extra_large")
    color_scheme: Optional[str] = Field(None, description="Color scheme: dark, dim, custom")


@router.get("/config")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_night_mode_config(
    user_id: str = Query(..., description="User ID"),
    current_user: dict = Depends(require_auth),
    night_mode_service: NightModeService = Depends(get_night_mode_service_dependency)
):
    """Get night mode configuration"""
    config = night_mode_service.get_night_mode_config(user_id)
    
    if not config:
        return {
            "message": "Night mode config not found",
            "config": None
        }
    
    return {
        "config": config
    }


@router.put("/config")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def update_night_mode_config(
    request: UpdateNightModeConfigRequest,
    current_user: dict = Depends(require_auth),
    night_mode_service: NightModeService = Depends(get_night_mode_service_dependency)
):
    """Update night mode configuration"""
    config = night_mode_service.update_night_mode_config(
        user_id=request.user_id,
        user_type=request.user_type,
        enabled=request.enabled,
        brightness=request.brightness,
        sound_enabled=request.sound_enabled,
        text_prompts=request.text_prompts,
        start_time=request.start_time,
        end_time=request.end_time,
        sound_type=request.sound_type,
        volume=request.volume,
        font_size=request.font_size,
        color_scheme=request.color_scheme,
        org_id=current_user.get("org_id")
    )
    
    return {
        "message": "Night mode config updated successfully",
        "config": config
    }


@router.get("/active")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def check_night_mode_active(
    user_id: str = Query(..., description="User ID"),
    current_user: dict = Depends(require_auth),
    night_mode_service: NightModeService = Depends(get_night_mode_service_dependency)
):
    """Check whether night mode is active"""
    is_active = night_mode_service.is_night_mode_active(user_id)
    
    return {
        "user_id": user_id,
        "is_active": is_active
    }
