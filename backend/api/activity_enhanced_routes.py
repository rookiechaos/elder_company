"""
Enhanced Activity API Routes - Advanced features
Enhanced Activity API Routes - Advanced features
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from utils.time_utils import utc_now

from services.activity_enhanced import ActivityEnhancedService
from services.logging_service import logger
from config.database import get_db
import uuid

router = APIRouter(prefix="/api/activities/enhanced", tags=["activities-enhanced"])


class CustomActivityRequest(BaseModel):
    """Create custom activity request"""
    title_ja: str
    title_zh: str
    title_en: Optional[str] = None
    description_ja: Optional[str] = None
    description_zh: Optional[str] = None
    category: str = "custom"
    tags: Optional[List[str]] = []
    difficulty_level: str = "medium"
    duration_minutes: Optional[int] = None
    required_materials: Optional[List[str]] = []
    participant_count: str = "1-2"
    suitable_for: Optional[List[str]] = []
    steps: Optional[List[str]] = []
    tips: Optional[str] = None
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []


class ActivityCustomizationRequest(BaseModel):
    """Activity customization request"""
    template_id: str
    customizations: Dict[str, Any]  # Customization content


class ActivityPlanRequest(BaseModel):
    """Activity plan request"""
    title: str
    description: Optional[str] = None
    activities: List[Dict[str, Any]]  # [{"activity_id": "...", "scheduled_date": "...", "notes": "..."}]
    start_date: str  # ISO format
    end_date: Optional[str] = None
    frequency: str = "daily"  # daily, weekly, custom


class EffectTrackingRequest(BaseModel):
    """Activity effectiveness tracking request"""
    mood_improvement: Optional[float] = None  # -1 to 1
    engagement_score: Optional[float] = None  # 0 to 10
    physical_benefit: Optional[float] = None  # 0 to 10
    cognitive_benefit: Optional[float] = None  # 0 to 10
    social_benefit: Optional[float] = None  # 0 to 10
    overall_satisfaction: Optional[float] = None  # 0 to 10
    follow_up_needed: Optional[bool] = False
    notes: Optional[str] = None


class ShareActivityRequest(BaseModel):
    """Share activity request"""
    share_type: str = "public"  # public, org, private
    org_id: Optional[str] = None
    allow_copy: bool = True


class CollaborativeDesignRequest(BaseModel):
    """Collaborative design request"""
    activity_id: Optional[str] = None  # If empty, create a new activity
    participants: List[Dict[str, str]]  # [{"user_id": "...", "role": "caregiver/elder/family"}]
    design_data: Dict[str, Any]  # Design content
    notes: Optional[str] = None


class FamilyParticipationRequest(BaseModel):
    """Family participation request"""
    family_member_id: str
    family_member_name: str
    relationship: str  # Relationship: child, spouse, etc.
    participation_type: str  # view, comment, participate
    feedback: Optional[str] = None


# ==================== Custom Activity ====================

@router.post("/custom")
async def create_custom_activity(
    caregiver_id: str,
    activity_data: CustomActivityRequest,
    org_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create custom activity"""
    try:
        service = ActivityEnhancedService(db)
        
        activity = service.create_custom_activity(
            caregiver_id=caregiver_id,
            activity_data=activity_data.dict(),
            org_id=org_id
        )
        
        return {
            "message": "Custom activity created successfully",
            "activity": activity
        }
    except Exception as e:
        logger.log_error(e, {"action": "create_custom_activity"})
        raise HTTPException(status_code=500, detail=f"Failed to create custom activity: {str(e)}")


@router.post("/customize")
async def customize_activity(
    customization: ActivityCustomizationRequest,
    caregiver_id: str,
    db: Session = Depends(get_db)
):
    """Customize activity from template"""
    try:
        service = ActivityEnhancedService(db)
        
        customized = service.customize_activity_from_template(
            template_id=customization.template_id,
            customizations=customization.customizations,
            caregiver_id=caregiver_id
        )
        
        return {
            "message": "Activity customized successfully",
            "customized_activity": customized
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.log_error(e, {"action": "customize_activity"})
        raise HTTPException(status_code=500, detail=f"Failed to customize activity: {str(e)}")


# ==================== Activity Planning ====================

@router.post("/plans")
async def create_activity_plan(
    caregiver_id: str,
    elder_id: str,
    plan_data: ActivityPlanRequest,
    org_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create activity plan"""
    try:
        service = ActivityEnhancedService(db)
        
        plan = service.create_activity_plan(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            plan_data=plan_data.dict(),
            org_id=org_id
        )
        
        return {
            "message": "Activity plan created successfully",
            "plan": plan
        }
    except Exception as e:
        logger.log_error(e, {"action": "create_activity_plan"})
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")


@router.get("/plans")
async def get_activity_plans(
    caregiver_id: Optional[str] = Query(None),
    elder_id: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get activity plan list"""
    try:
        service = ActivityEnhancedService(db)
        
        plans = service.get_activity_plans(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id
        )
        
        return {
            "plans": plans,
            "count": len(plans)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_plans"})
        raise HTTPException(status_code=500, detail=f"Failed to get plans: {str(e)}")


# ==================== Effect Tracking ====================

@router.post("/records/{record_id}/effects")
async def track_activity_effects(
    record_id: str,
    effect_data: EffectTrackingRequest,
    db: Session = Depends(get_db)
):
    """Track activity effectiveness"""
    try:
        service = ActivityEnhancedService(db)
        
        tracking = service.track_activity_effects(
            record_id=record_id,
            effect_data=effect_data.dict()
        )
        
        return {
            "message": "Activity effects tracked successfully",
            "tracking": tracking
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.log_error(e, {"action": "track_activity_effects"})
        raise HTTPException(status_code=500, detail=f"Failed to track effects: {str(e)}")


@router.get("/effects/analysis")
async def get_activity_effect_analysis(
    elder_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get activity effectiveness analysis"""
    try:
        service = ActivityEnhancedService(db)
        
        analysis = service.get_activity_effect_analysis(
            elder_id=elder_id,
            days=days
        )
        
        return analysis
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_effect_analysis"})
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


# ==================== Activity Sharing ====================

@router.post("/{activity_id}/share")
async def share_activity(
    activity_id: str,
    share_settings: ShareActivityRequest,
    shared_by: str,
    db: Session = Depends(get_db)
):
    """Share activity to community"""
    try:
        service = ActivityEnhancedService(db)
        
        share_info = service.share_activity(
            activity_id=activity_id,
            shared_by=shared_by,
            share_settings=share_settings.dict()
        )
        
        return {
            "message": "Activity shared successfully",
            "share_info": share_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.log_error(e, {"action": "share_activity"})
        raise HTTPException(status_code=500, detail=f"Failed to share activity: {str(e)}")


@router.get("/shared")
async def get_shared_activities(
    org_id: Optional[str] = Query(None),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get community-shared activities"""
    try:
        service = ActivityEnhancedService(db)
        
        activities = service.get_shared_activities(
            org_id=org_id,
            limit=limit
        )
        
        return {
            "activities": activities,
            "count": len(activities)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_shared_activities"})
        raise HTTPException(status_code=500, detail=f"Failed to get shared activities: {str(e)}")


# ==================== Collaborative Design ====================

@router.post("/collaborate/design")
async def collaborative_design(
    design_request: CollaborativeDesignRequest,
    db: Session = Depends(get_db)
):
    """Collaboratively design activity"""
    try:
        from services.activity_service import ActivityService
        
        activity_service = ActivityService(db)
        enhanced_service = ActivityEnhancedService(db)
        
        # Create or update activity with collaborative design
        if design_request.activity_id:
            # Update existing activity
            activity = activity_service.get_activity_template(design_request.activity_id)
            if not activity:
                raise HTTPException(status_code=404, detail="Activity not found")
        else:
            # Create new activity
            activity_data = {
                "title_zh": design_request.design_data.get("title_zh", "Collaboratively design activity"),
                "title_ja": design_request.design_data.get("title_ja", ""),
                "category": design_request.design_data.get("category", "custom"),
                "steps": design_request.design_data.get("steps", []),
                **design_request.design_data
            }
            
            # Get caregiver_id from participants
            caregiver = next((p for p in design_request.participants if p.get("role") == "caregiver"), None)
            caregiver_id = caregiver.get("user_id") if caregiver else "system"
            
            activity = enhanced_service.create_custom_activity(
                caregiver_id=caregiver_id,
                activity_data=activity_data
            )
        
        # Store collaborative design info in activity record
        from models.database import ActivityRecordDB
        record = ActivityRecordDB(
            record_id=f"collab_{uuid.uuid4().hex[:12]}",
            caregiver_id=caregiver_id,
            activity_title=activity.get("title_zh", "Co-design"),
            activity_category="collaborative_design",
            co_designed_by=design_request.participants,
            design_notes=design_request.notes
        )
        
        db.add(record)
        db.commit()
        
        return {
            "message": "Collaborative design saved successfully",
            "activity": activity,
            "participants": design_request.participants
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "collaborative_design"})
        raise HTTPException(status_code=500, detail=f"Failed to save collaborative design: {str(e)}")


# ==================== Family Participation ====================

@router.post("/records/{record_id}/family")
async def add_family_participation(
    record_id: str,
    participation: FamilyParticipationRequest,
    db: Session = Depends(get_db)
):
    """Add family participation"""
    try:
        from models.database import ActivityRecordDB
        
        record = db.query(ActivityRecordDB).filter(
            ActivityRecordDB.record_id == record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Activity record not found")
        
        # Add family member
        family_members = record.family_members or []
        family_members.append({
            "family_member_id": participation.family_member_id,
            "name": participation.family_member_name,
            "relationship": participation.relationship,
            "participation_type": participation.participation_type,
            "joined_at": utc_now().isoformat()
        })
        record.family_members = family_members
        
        # Add feedback if provided
        if participation.feedback:
            family_feedback = record.family_feedback or []
            family_feedback.append({
                "family_member_id": participation.family_member_id,
                "feedback": participation.feedback,
                "timestamp": utc_now().isoformat()
            })
            record.family_feedback = family_feedback
        
        db.commit()
        db.refresh(record)
        
        return {
            "message": "Family participation added successfully",
            "family_members": record.family_members
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "add_family_participation"})
        raise HTTPException(status_code=500, detail=f"Failed to add family participation: {str(e)}")


@router.get("/records/{record_id}/family")
async def get_family_participation(
    record_id: str,
    db: Session = Depends(get_db)
):
    """Get family participation info"""
    try:
        from models.database import ActivityRecordDB
        
        record = db.query(ActivityRecordDB).filter(
            ActivityRecordDB.record_id == record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Activity record not found")
        
        return {
            "family_members": record.family_members or [],
            "family_feedback": record.family_feedback or []
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_family_participation"})
        raise HTTPException(status_code=500, detail=f"Failed to get family participation: {str(e)}")


# ==================== Multimedia Upload ====================

@router.post("/upload/image")
async def upload_activity_image(
    file: UploadFile = File(...),
    activity_id: Optional[str] = None
):
    """Upload activity image"""
    # TODO: Implement file upload to storage (S3, local, etc.)
    # For now, return placeholder
    return {
        "message": "Image upload endpoint - to be implemented",
        "filename": file.filename,
        "activity_id": activity_id
    }


@router.post("/upload/video")
async def upload_activity_video(
    file: UploadFile = File(...),
    activity_id: Optional[str] = None
):
    """Upload activity video"""
    # TODO: Implement file upload to storage
    return {
        "message": "Video upload endpoint - to be implemented",
        "filename": file.filename,
        "activity_id": activity_id
    }
