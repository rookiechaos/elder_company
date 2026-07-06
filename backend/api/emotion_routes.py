"""
Emotion Logging API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from dependencies import require_auth, get_emotion_service_dependency
from services.emotion_service import EmotionService
from middleware.rate_limit import rate_limit, RATE_LIMITS
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError

router = APIRouter(prefix="/api/emotions", tags=["emotions"])


class LogEmotionRequest(BaseModel):
    """Record emotion request"""
    user_id: str
    user_type: str = Field(..., description="User type: elder, caregiver")
    emotion_score: int = Field(..., ge=1, le=5, description="Emotion score: 1-5")
    emotion_type: Optional[str] = Field(None, description="Emotion type: happy, sad, anxious, calm, etc.")
    notes: Optional[str] = Field(None, max_length=500)
    voice_note_url: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    related_task_id: Optional[str] = None
    related_schedule_id: Optional[str] = None
    related_activity_id: Optional[str] = None
    
    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in ['elder', 'caregiver']:
            raise ValueError("User type must be 'elder' or 'caregiver'")
        return v


class PositiveFeedbackRequest(BaseModel):
    """Positive feedback request"""
    elder_id: str
    caregiver_id: str
    context: Dict[str, Any]  # Includes completed_tasks, emotion_score, recent_activities, etc.


class StressDetectionRequest(BaseModel):
    """Stress detection request"""
    caregiver_id: str
    emotion_logs: List[Dict[str, Any]]  # Recent emotion logs
    workload: Optional[Dict[str, Any]] = None


@router.post("/log")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def log_emotion(
    request: LogEmotionRequest,
    current_user: dict = Depends(require_auth),
    emotion_service: EmotionService = Depends(get_emotion_service_dependency)
):
    """Record emotion"""
    # Validate user ID (may only record self or linked elder)
    user_id_from_token = current_user.get("user_id")
    if request.user_type == "caregiver" and request.user_id != user_id_from_token:
        raise HTTPException(status_code=403, detail="Can only log your own emotion as caregiver")
    
    emotion_log = emotion_service.log_emotion(
        user_id=request.user_id,
        user_type=request.user_type,
        emotion_score=request.emotion_score,
        emotion_type=request.emotion_type,
        notes=request.notes,
        voice_note_url=request.voice_note_url,
        context=request.context,
        related_task_id=request.related_task_id,
        related_schedule_id=request.related_schedule_id,
        related_activity_id=request.related_activity_id,
        org_id=current_user.get("org_id")
    )
    
    return {
        "message": "Emotion logged successfully",
        "emotion_log": emotion_log
    }


@router.get("/history")
@rate_limit(limit=RATE_LIMITS.get("default", "60/minute"))
@handle_api_errors
async def get_emotion_history(
    user_id: str = Query(..., description="User ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    user_type: Optional[str] = Query(None, description="User type: elder, caregiver"),
    current_user: dict = Depends(require_auth),
    emotion_service: EmotionService = Depends(get_emotion_service_dependency)
):
    """Get emotion history"""
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
    
    history = emotion_service.get_emotion_history(
        user_id=user_id,
        start_date=start_dt,
        end_date=end_dt,
        user_type=user_type
    )
    
    return {
        "emotion_logs": history,
        "count": len(history)
    }


@router.get("/analysis")
@rate_limit(limit=RATE_LIMITS.get("default", "30/minute"))
@handle_api_errors
async def get_emotion_analysis(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    user_type: Optional[str] = Query(None, description="User type: elder, caregiver"),
    current_user: dict = Depends(require_auth),
    emotion_service: EmotionService = Depends(get_emotion_service_dependency)
):
    """Get emotion analysis"""
    analysis = emotion_service.get_emotion_analysis(
        user_id=user_id,
        days=days,
        user_type=user_type
    )
    
    return analysis


@router.post("/positive-feedback")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def generate_positive_feedback(
    request: PositiveFeedbackRequest,
    current_user: dict = Depends(require_auth),
    emotion_service: EmotionService = Depends(get_emotion_service_dependency)
):
    """Generate positive feedback"""
    feedback = emotion_service.generate_positive_feedback(
        elder_id=request.elder_id,
        caregiver_id=request.caregiver_id,
        context=request.context
    )
    
    return {
        "feedback": feedback,
        "elder_id": request.elder_id,
        "caregiver_id": request.caregiver_id
    }


@router.post("/stress-detection")
@rate_limit(limit=RATE_LIMITS.get("default", "20/minute"))
@handle_api_errors
async def detect_stress(
    request: StressDetectionRequest,
    current_user: dict = Depends(require_auth),
    emotion_service: EmotionService = Depends(get_emotion_service_dependency)
):
    """Detect stress signals"""
    stress_result = emotion_service.detect_stress(
        caregiver_id=request.caregiver_id,
        emotion_logs=request.emotion_logs,
        workload=request.workload
    )
    
    return stress_result
