"""
Activity Management API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from services.activity_service import ActivityService
from services.logging_service import logger
from config.database import get_db

router = APIRouter(prefix="/api/activities", tags=["activities"])


class ElderProfileRequest(BaseModel):
    """Elder info model (for activity recommendations)"""
    interests: Optional[List[str]] = []  # Interests: e.g. ["crafts", "music", "exercise"]
    abilities: Optional[List[str]] = []  # Abilities: e.g. ["can sit", "can use hands"]
    health_conditions: Optional[List[str]] = []  # Health conditions: e.g. ["dementia", "limited mobility"]
    mobility_level: Optional[str] = "normal"  # normal, limited, bedridden
    cognitive_level: Optional[str] = "normal"  # normal, mild_impairment, impaired
    preferences: Optional[Dict[str, Any]] = {}  # Other preferences


class ActivityRecordRequest(BaseModel):
    """Activity record request model"""
    activity_template_id: Optional[str] = None
    activity_title: str
    activity_category: Optional[str] = None
    customized_steps: Optional[List[str]] = None
    materials_used: Optional[List[str]] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    elder_engagement: Optional[str] = None  # high, medium, low
    elder_mood_before: Optional[str] = None
    elder_mood_after: Optional[str] = None
    caregiver_feedback: Optional[str] = None
    elder_feedback: Optional[str] = None
    photos: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    activity_date: Optional[str] = None  # ISO format


@router.get("/templates")
async def get_activity_templates(
    category: Optional[str] = Query(None, description="Activity category"),
    difficulty: Optional[str] = Query(None, description="Difficulty: easy, medium, hard"),
    tags: Optional[str] = Query(None, description="Tags (comma-separated)"),
    limit: int = Query(50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get activity template list"""
    try:
        activity_service = ActivityService(db)
        
        tag_list = tags.split(",") if tags else None
        
        templates = activity_service.get_activity_templates(
            category=category,
            difficulty=difficulty,
            tags=tag_list,
            limit=limit
        )
        
        return {
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_templates"})
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/templates/{activity_id}")
async def get_activity_template(
    activity_id: str,
    db: Session = Depends(get_db)
):
    """Get single activity template details"""
    try:
        activity_service = ActivityService(db)
        template = activity_service.get_activity_template(activity_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="Activity template not found")
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_template", "activity_id": activity_id})
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.post("/recommend")
async def recommend_activities(
    caregiver_id: str,
    elder_profile: ElderProfileRequest,
    org_id: Optional[str] = None,
    elder_id: Optional[str] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Recommend activities based on elder profile"""
    try:
        activity_service = ActivityService(db)
        
        recommendation = activity_service.recommend_activities(
            caregiver_id=caregiver_id,
            elder_profile=elder_profile.dict(),
            org_id=org_id,
            elder_id=elder_id,
            limit=limit
        )
        
        logger.log_api_request(
            endpoint="/api/activities/recommend",
            method="POST",
            user_id=caregiver_id,
            org_id=org_id,
            status_code=200,
            response_time_ms=0
        )
        
        return recommendation
    except Exception as e:
        logger.log_error(e, {
            "action": "recommend_activities",
            "caregiver_id": caregiver_id
        })
        raise HTTPException(status_code=500, detail=f"Failed to recommend activities: {str(e)}")


@router.post("/records")
async def create_activity_record(
    caregiver_id: str,
    activity_data: ActivityRecordRequest,
    org_id: Optional[str] = None,
    elder_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create activity record"""
    try:
        activity_service = ActivityService(db)
        
        record_data = activity_data.dict()
        if record_data.get("activity_date"):
            record_data["activity_date"] = datetime.fromisoformat(record_data["activity_date"])
        
        record = activity_service.create_activity_record(
            caregiver_id=caregiver_id,
            activity_data=record_data,
            org_id=org_id,
            elder_id=elder_id
        )
        
        logger.log_api_request(
            endpoint="/api/activities/records",
            method="POST",
            user_id=caregiver_id,
            org_id=org_id,
            status_code=200,
            response_time_ms=0
        )
        
        return {
            "message": "Activity record created successfully",
            "record": record
        }
    except Exception as e:
        logger.log_error(e, {
            "action": "create_activity_record",
            "caregiver_id": caregiver_id
        })
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")


@router.get("/records")
async def get_activity_records(
    caregiver_id: Optional[str] = Query(None),
    elder_id: Optional[str] = Query(None),
    org_id: Optional[str] = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    """Get activity record list"""
    try:
        activity_service = ActivityService(db)
        
        records = activity_service.get_activity_records(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            limit=limit
        )
        
        return {
            "records": records,
            "count": len(records)
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_records"})
        raise HTTPException(status_code=500, detail=f"Failed to get records: {str(e)}")


@router.get("/records/{record_id}")
async def get_activity_record(
    record_id: str,
    db: Session = Depends(get_db)
):
    """Get single activity record details"""
    try:
        from models.database import ActivityRecordDB
        
        record = db.query(ActivityRecordDB).filter(
            ActivityRecordDB.record_id == record_id
        ).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="Activity record not found")
        
        activity_service = ActivityService(db)
        return activity_service._record_to_dict(record)
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_record", "record_id": record_id})
        raise HTTPException(status_code=500, detail=f"Failed to get record: {str(e)}")


@router.get("/categories")
async def get_activity_categories(db: Session = Depends(get_db)):
    """Get activity category list"""
    try:
        from models.database import ActivityTemplateDB
        from sqlalchemy import distinct
        
        categories = db.query(
            distinct(ActivityTemplateDB.category)
        ).all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return {
            "categories": category_list,
            "descriptions": {
                "cognitive": {"en": "Cognitive training", "ja": "認知トレーニング"},
                "craft": {"en": "Crafts", "ja": "手工芸"},
                "music": {"en": "Music", "ja": "音楽"},
                "exercise": {"en": "Exercise", "ja": "運動"},
                "social": {"en": "Social activities", "ja": "社交"},
                "reminiscence": {"en": "Reminiscence", "ja": "回想"}
            }
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_activity_categories"})
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")
