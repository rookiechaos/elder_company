"""
Organization Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from services.organization_service import OrganizationService
from services.logging_service import logger
from config.database import get_db

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


class OrganizationRequest(BaseModel):
    """Organization create/update request model"""
    name: str
    name_ja: Optional[str] = None
    org_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    default_source_language: Optional[str] = "ja"
    default_target_language: Optional[str] = "zh"
    org_custom_terms: Optional[Dict[str, str]] = None
    org_care_scenarios: Optional[List[str]] = None
    subscription_plan: Optional[str] = "basic"
    max_users: Optional[int] = 10
    monthly_translation_limit: Optional[int] = 1000


@router.post("")
async def create_organization(
    org_data: OrganizationRequest,
    db: Session = Depends(get_db)
):
    """Create new organization"""
    try:
        org_service = OrganizationService(db)
        
        # Generate org_id
        import uuid
        org_id = f"org_{uuid.uuid4().hex[:12]}"
        
        org_dict = org_data.dict()
        org_dict["org_id"] = org_id
        org_dict["is_active"] = True
        
        organization = org_service.create_organization(org_dict)
        
        logger.log_organization_event("created", org_id, {"name": org_data.name})
        
        return {
            "message": "Organization created successfully",
            "organization": organization
        }
    except Exception as e:
        logger.log_error(e, {"action": "create_organization"})
        raise HTTPException(status_code=500, detail=f"Failed to create organization: {str(e)}")


@router.get("/{org_id}")
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Get organization information"""
    try:
        org_service = OrganizationService(db)
        organization = org_service.get_organization(org_id)
        
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return organization
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_organization", "org_id": org_id})
        raise HTTPException(status_code=500, detail=f"Failed to get organization: {str(e)}")


@router.put("/{org_id}")
async def update_organization(
    org_id: str,
    org_data: OrganizationRequest,
    db: Session = Depends(get_db)
):
    """Update organization information"""
    try:
        org_service = OrganizationService(db)
        
        update_dict = org_data.dict(exclude_unset=True)
        organization = org_service.update_organization(org_id, update_dict)
        
        logger.log_organization_event("updated", org_id, update_dict)
        
        return {
            "message": "Organization updated successfully",
            "organization": organization
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.log_error(e, {"action": "update_organization", "org_id": org_id})
        raise HTTPException(status_code=500, detail=f"Failed to update organization: {str(e)}")


@router.get("/{org_id}/users")
async def get_organization_users(
    org_id: str,
    db: Session = Depends(get_db)
):
    """Get all users in organization"""
    try:
        org_service = OrganizationService(db)
        users = org_service.get_organization_users(org_id)
        
        return {
            "org_id": org_id,
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_organization_users", "org_id": org_id})
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


@router.get("/{org_id}/statistics")
async def get_organization_statistics(
    org_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get organization usage statistics"""
    try:
        org_service = OrganizationService(db)
        stats = org_service.get_organization_statistics(org_id, days=days)
        
        return stats
    except Exception as e:
        logger.log_error(e, {"action": "get_organization_statistics", "org_id": org_id})
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
