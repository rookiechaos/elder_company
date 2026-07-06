"""
Data Synchronization API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from services.sync_service import SyncService
from dependencies import require_auth, get_sync_service_dependency
from services.logging_service import logger
from config.database import get_db
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors

router = APIRouter(prefix="/api/sync", tags=["synchronization"])


class SyncDataRequest(BaseModel):
    """Sync data request"""
    profile: Optional[Dict[str, Any]] = None
    activities: Optional[List[Dict[str, Any]]] = None
    translations: Optional[List[Dict[str, Any]]] = None


def get_device_id(
    x_device_id: Optional[str] = Header(None, alias="X-Device-ID")
) -> str:
    """Get device ID from header"""
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Device ID is required")
    return x_device_id


@router.post("/full")
@rate_limit(limit=RATE_LIMITS["sync"])
@handle_api_errors
async def full_sync(
    sync_data: SyncDataRequest,
    request: Request,
    current_user: dict = Depends(require_auth),
    device_id: str = Depends(get_device_id),
    sync_service: SyncService = Depends(get_sync_service_dependency)
):
    """Full data sync"""
    try:
        
        local_data = {
            "profile": sync_data.profile,
            "activities": sync_data.activities,
            "translations": sync_data.translations
        }
        
        result = sync_service.full_sync(
            user_id=current_user["user_id"],
            device_id=device_id,
            local_data=local_data
        )
        
        logger.log_api_request(
            endpoint="/api/sync/full",
            method="POST",
            user_id=current_user["user_id"],
            org_id=None,
            status_code=200,
            response_time_ms=0
        )
        
        return result
    except Exception as e:
        logger.log_error(e, {
            "action": "full_sync",
            "user_id": current_user["user_id"]
        })
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/profile")
@handle_api_errors
async def sync_profile(
    profile_data: Dict[str, Any],
    current_user: dict = Depends(require_auth),
    device_id: str = Depends(get_device_id),
    sync_service: SyncService = Depends(get_sync_service_dependency)
):
    """Sync user configuration"""
    try:
        
        result = sync_service.sync_user_profile(
            user_id=current_user["user_id"],
            device_id=device_id,
            local_data=profile_data
        )
        
        return result
    except Exception as e:
        logger.log_error(e, {"action": "sync_profile"})
        raise HTTPException(status_code=500, detail=f"Profile sync failed: {str(e)}")


@router.post("/activities")
@handle_api_errors
async def sync_activities(
    activities: List[Dict[str, Any]],
    current_user: dict = Depends(require_auth),
    device_id: str = Depends(get_device_id),
    sync_service: SyncService = Depends(get_sync_service_dependency)
):
    """Sync activity records"""
    try:
        
        result = sync_service.sync_activity_records(
            user_id=current_user["user_id"],
            device_id=device_id,
            local_records=activities
        )
        
        return result
    except Exception as e:
        logger.log_error(e, {"action": "sync_activities"})
        raise HTTPException(status_code=500, detail=f"Activities sync failed: {str(e)}")


@router.post("/translations")
@handle_api_errors
async def sync_translations(
    translations: List[Dict[str, Any]],
    current_user: dict = Depends(require_auth),
    device_id: str = Depends(get_device_id),
    sync_service: SyncService = Depends(get_sync_service_dependency)
):
    """Sync translation history"""
    try:
        
        result = sync_service.sync_translation_history(
            user_id=current_user["user_id"],
            device_id=device_id,
            local_history=translations
        )
        
        return result
    except Exception as e:
        logger.log_error(e, {"action": "sync_translations"})
        raise HTTPException(status_code=500, detail=f"Translations sync failed: {str(e)}")


@router.get("/status")
@handle_api_errors
async def get_sync_status(
    current_user: dict = Depends(require_auth),
    device_id: str = Depends(get_device_id),
    sync_service: SyncService = Depends(get_sync_service_dependency)
):
    """Get sync status"""
    try:
        
        status = sync_service.get_sync_status(
            user_id=current_user["user_id"],
            device_id=device_id
        )
        
        return status
    except Exception as e:
        logger.log_error(e, {"action": "get_sync_status"})
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")
