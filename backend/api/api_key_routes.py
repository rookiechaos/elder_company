"""
API Key Management Routes
API Key Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from dependencies import require_auth, get_api_key_service_dependency
from services.api_key_service import ApiKeyService
from middleware.api_decorators import handle_api_errors
from exceptions import NotFoundError, AuthenticationError
from config.database import get_db

router = APIRouter(prefix="/api/api-keys", tags=["api-keys"])


class CreateApiKeyRequest(BaseModel):
    """Create API key request"""
    key_name: Optional[str] = None
    key_type: str = "user"  # user, org, system
    permissions: Optional[Dict[str, Any]] = None
    rate_limit: str = "100/minute"
    max_requests_per_day: Optional[int] = None
    expires_in_days: Optional[int] = None  # None = never expires


class UpdateApiKeyRequest(BaseModel):
    """Update API key request"""
    key_name: Optional[str] = None
    rate_limit: Optional[str] = None
    max_requests_per_day: Optional[int] = None
    expires_in_days: Optional[int] = None


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_service: ApiKeyService = Depends(get_api_key_service_dependency)
) -> Dict[str, Any]:
    """Verify API key from header"""
    if not x_api_key:
        raise AuthenticationError("API key required. Please provide X-API-Key header.")
    
    key_info = api_key_service.verify_api_key(x_api_key)
    
    if not key_info:
        raise AuthenticationError("Invalid or expired API key")
    
    return key_info


@router.post("")
@handle_api_errors
async def create_api_key(
    request: CreateApiKeyRequest,
    current_user: dict = Depends(require_auth),
    api_key_service: ApiKeyService = Depends(get_api_key_service_dependency)
):
    """Create a new API key"""
    result = api_key_service.create_api_key(
        user_id=current_user.get("user_id"),
        org_id=current_user.get("org_id"),
        key_name=request.key_name,
        key_type=request.key_type,
        permissions=request.permissions,
        rate_limit=request.rate_limit,
        max_requests_per_day=request.max_requests_per_day,
        expires_in_days=request.expires_in_days
    )
    
    return result


@router.get("")
@handle_api_errors
async def list_api_keys(
    current_user: dict = Depends(require_auth),
    api_key_service: ApiKeyService = Depends(get_api_key_service_dependency)
):
    """Get user's API key list"""
    keys = api_key_service.get_api_keys(
        user_id=current_user.get("user_id"),
        org_id=current_user.get("org_id")
    )
    
    return {
        "api_keys": keys,
        "count": len(keys)
    }


@router.put("/{key_id}")
@handle_api_errors
async def update_api_key(
    key_id: int,
    request: UpdateApiKeyRequest,
    current_user: dict = Depends(require_auth),
    api_key_service: ApiKeyService = Depends(get_api_key_service_dependency)
):
    """Update API key settings"""
    result = api_key_service.update_api_key(
        key_id=key_id,
        key_name=request.key_name,
        rate_limit=request.rate_limit,
        max_requests_per_day=request.max_requests_per_day,
        expires_in_days=request.expires_in_days
    )
    
    return result


@router.delete("/{key_id}")
@handle_api_errors
async def revoke_api_key(
    key_id: int,
    current_user: dict = Depends(require_auth),
    api_key_service: ApiKeyService = Depends(get_api_key_service_dependency)
):
    """Revoke (deactivate) API key"""
    success = api_key_service.revoke_api_key(key_id)
    
    if not success:
        raise NotFoundError(f"API key {key_id} not found")
    
    return {
        "message": f"API key {key_id} revoked successfully",
        "key_id": key_id
    }
