"""
Emergency API Routes
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_emergency_service_dependency
from services.emergency_service import EmergencyService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError

router = APIRouter(prefix="/api/emergency", tags=["emergency"])


class RecordEmergencyRequest(BaseModel):
    """Record emergency request"""
    elder_id: str = Field(..., min_length=1)
    caregiver_id: str = Field(..., min_length=1)
    emergency_type: str = Field(..., description="Emergency type: health, emotional, behavioral")
    severity: str = Field(..., description="Severity: low, medium, high")
    description: str = Field(..., min_length=1, max_length=1000)
    actions_taken: Optional[List[str]] = None
    generate_guidance: bool = Field(True, description="Whether to generate AI guidance")
    generate_summary: bool = Field(True, description="Whether to generate a brief report")
    
    @validator('emergency_type')
    def validate_emergency_type(cls, v):
        valid_types = ['health', 'emotional', 'behavioral']
        if v not in valid_types:
            raise ValueError(f'Emergency type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['low', 'medium', 'high']
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v


class GetGuidanceRequest(BaseModel):
    """Get AI guidance request"""
    elder_id: str = Field(..., min_length=1)
    emergency_type: str = Field(..., description="Emergency type: health, emotional, behavioral")
    current_situation: str = Field(..., min_length=1, max_length=500)
    language: Optional[str] = Field("ja", description="Disclaimer language: zh, ja, en")
    
    @validator('emergency_type')
    def validate_emergency_type(cls, v):
        valid_types = ['health', 'emotional', 'behavioral']
        if v not in valid_types:
            raise ValueError(f'Emergency type must be one of: {", ".join(valid_types)}')
        return v


@router.post("/record")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def record_emergency(
    request: RecordEmergencyRequest,
    current_user: dict = Depends(require_auth),
    emergency_service: EmergencyService = Depends(get_emergency_service_dependency)
):
    """Record an emergency"""
    record = emergency_service.record_emergency(
        elder_id=request.elder_id,
        caregiver_id=request.caregiver_id,
        emergency_type=request.emergency_type,
        severity=request.severity,
        description=request.description,
        actions_taken=request.actions_taken,
        org_id=current_user.get("org_id"),
        generate_guidance=request.generate_guidance,
        generate_summary=request.generate_summary
    )
    
    return {
        "message": "Emergency recorded successfully",
        "record": record
    }


@router.post("/guidance")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def get_emergency_guidance(
    request: GetGuidanceRequest,
    current_user: dict = Depends(require_auth),
    emergency_service: EmergencyService = Depends(get_emergency_service_dependency)
):
    """Get AI emergency guidance"""
    guidance = emergency_service.get_emergency_guidance(
        elder_id=request.elder_id,
        emergency_type=request.emergency_type,
        current_situation=request.current_situation,
        language=request.language or "ja"
    )
    
    return guidance


@router.get("/history")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_emergency_history(
    elder_id: Optional[str] = Query(None),
    caregiver_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_auth),
    emergency_service: EmergencyService = Depends(get_emergency_service_dependency)
):
    """Get emergency history"""
    # Parse dates
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid start_date format")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except Exception:
            raise ValidationError("Invalid end_date format")
    
    records = emergency_service.get_emergency_history(
        elder_id=elder_id,
        caregiver_id=caregiver_id,
        start_date=start_dt,
        end_date=end_dt,
        org_id=current_user.get("org_id"),
        limit=limit
    )
    
    return {
        "records": records,
        "count": len(records)
    }
