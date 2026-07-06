"""
Enhanced Activity Service - Advanced features for activity management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
import uuid
import json

from models.database import (
    ActivityTemplateDB, ActivityRecordDB, ActivityRecommendationDB
)
from services.cache_service import get_cache, CACHE_TTL


class ActivityEnhancedService:
    """Enhanced activity service with advanced features"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Activity Customization ====================
    
    def create_custom_activity(
        self,
        caregiver_id: str,
        activity_data: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a custom activity template"""
        activity_id = f"custom_{uuid.uuid4().hex[:12]}"
        
        activity = ActivityTemplateDB(
            activity_id=activity_id,
            title_ja=activity_data.get("title_ja", ""),
            title_zh=activity_data.get("title_zh", ""),
            title_en=activity_data.get("title_en"),
            description_ja=activity_data.get("description_ja"),
            description_zh=activity_data.get("description_zh"),
            category=activity_data.get("category", "custom"),
            tags=activity_data.get("tags", []),
            difficulty_level=activity_data.get("difficulty_level", "medium"),
            duration_minutes=activity_data.get("duration_minutes"),
            required_materials=activity_data.get("required_materials", []),
            participant_count=activity_data.get("participant_count", "1-2"),
            suitable_for=activity_data.get("suitable_for", []),
            health_considerations=activity_data.get("health_considerations", []),
            steps=activity_data.get("steps", []),
            tips=activity_data.get("tips"),
            variations=activity_data.get("variations", []),
            created_by=caregiver_id,
            usage_count=0,
            rating=0.0
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        # Invalidate cache
        cache = get_cache()
        cache.clear("activity:templates")
        
        return self._template_to_dict(activity)
    
    def customize_activity_from_template(
        self,
        template_id: str,
        customizations: Dict[str, Any],
        caregiver_id: str
    ) -> Dict[str, Any]:
        """Customize an activity from a template"""
        template = self.db.query(ActivityTemplateDB).filter(
            ActivityTemplateDB.activity_id == template_id
        ).first()
        
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Create customized version
        customized = {
            "title_zh": customizations.get("title_zh", template.title_zh),
            "title_ja": customizations.get("title_ja", template.title_ja),
            "description_zh": customizations.get("description_zh", template.description_zh),
            "steps": customizations.get("steps", template.steps or []),
            "materials": customizations.get("materials", template.required_materials or []),
            "duration": customizations.get("duration_minutes", template.duration_minutes),
            "difficulty": customizations.get("difficulty_level", template.difficulty_level),
            "notes": customizations.get("notes", "")
        }
        
        return customized
    
    # ==================== Activity Planning ====================
    
    def create_activity_plan(
        self,
        caregiver_id: str,
        elder_id: str,
        plan_data: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an activity plan (schedule)"""
        plan_id = f"plan_{uuid.uuid4().hex[:12]}"
        
        plan = {
            "plan_id": plan_id,
            "caregiver_id": caregiver_id,
            "elder_id": elder_id,
            "org_id": org_id,
            "title": plan_data.get("title", "Activity plan"),
            "description": plan_data.get("description"),
            "activities": plan_data.get("activities", []),  # List of activity IDs with schedule
            "start_date": plan_data.get("start_date"),
            "end_date": plan_data.get("end_date"),
            "frequency": plan_data.get("frequency", "daily"),  # daily, weekly, custom
            "status": "active",
            "created_at": utc_now().isoformat()
        }
        
        # Store in ActivityRecordDB with special type
        record = ActivityRecordDB(
            record_id=plan_id,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            activity_title=plan.get("title"),
            activity_category="plan",
            notes=json.dumps(plan, ensure_ascii=False),
            activity_date=datetime.fromisoformat(plan["start_date"]) if plan.get("start_date") else utc_now()
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return plan
    
    def get_activity_plans(
        self,
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get activity plans"""
        query = self.db.query(ActivityRecordDB).filter(
            ActivityRecordDB.activity_category == "plan"
        )
        
        if caregiver_id:
            query = query.filter(ActivityRecordDB.caregiver_id == caregiver_id)
        if elder_id:
            query = query.filter(ActivityRecordDB.elder_id == elder_id)
        if org_id:
            query = query.filter(ActivityRecordDB.org_id == org_id)
        
        records = query.order_by(desc(ActivityRecordDB.created_at)).all()
        
        plans = []
        for record in records:
            try:
                plan = json.loads(record.notes)
                plans.append(plan)
            except:
                pass
        
        return plans
    
    # ==================== Activity Effect Tracking ====================
    
    def track_activity_effects(
        self,
        record_id: str,
        effect_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track and analyze activity effects"""
        record = self.db.query(ActivityRecordDB).filter(
            ActivityRecordDB.record_id == record_id
        ).first()
        
        if not record:
            raise ValueError(f"Activity record {record_id} not found")
        
        # Update effect tracking data
        effect_tracking = {
            "mood_improvement": effect_data.get("mood_improvement"),  # -1 to 1
            "engagement_score": effect_data.get("engagement_score"),  # 0 to 10
            "physical_benefit": effect_data.get("physical_benefit"),  # 0 to 10
            "cognitive_benefit": effect_data.get("cognitive_benefit"),  # 0 to 10
            "social_benefit": effect_data.get("social_benefit"),  # 0 to 10
            "overall_satisfaction": effect_data.get("overall_satisfaction"),  # 0 to 10
            "follow_up_needed": effect_data.get("follow_up_needed", False),
            "notes": effect_data.get("notes")
        }
        
        # Store in notes or create separate tracking
        current_notes = record.notes or ""
        tracking_json = json.dumps(effect_tracking, ensure_ascii=False)
        record.notes = f"{current_notes}\n[Effect Tracking]: {tracking_json}"
        
        self.db.commit()
        self.db.refresh(record)
        
        return effect_tracking
    
    def get_activity_effect_analysis(
        self,
        elder_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analyze activity effects over time"""
        cutoff_date = utc_now() - timedelta(days=days)
        
        records = self.db.query(ActivityRecordDB).filter(
            ActivityRecordDB.elder_id == elder_id,
            ActivityRecordDB.activity_date >= cutoff_date
        ).all()
        
        # Analyze effects
        total_activities = len(records)
        mood_improvements = []
        engagement_scores = []
        satisfaction_scores = []
        
        for record in records:
            if record.notes and "[Effect Tracking]:" in record.notes:
                try:
                    tracking_json = record.notes.split("[Effect Tracking]:")[1].strip()
                    tracking = json.loads(tracking_json)
                    
                    if tracking.get("mood_improvement") is not None:
                        mood_improvements.append(tracking["mood_improvement"])
                    if tracking.get("engagement_score") is not None:
                        engagement_scores.append(tracking["engagement_score"])
                    if tracking.get("overall_satisfaction") is not None:
                        satisfaction_scores.append(tracking["overall_satisfaction"])
                except:
                    pass
        
        analysis = {
            "total_activities": total_activities,
            "tracked_activities": len(mood_improvements),
            "avg_mood_improvement": sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0,
            "avg_engagement": sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0,
            "avg_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0,
            "trend": "improving" if len(mood_improvements) > 1 and mood_improvements[-1] > mood_improvements[0] else "stable"
        }
        
        return analysis
    
    # ==================== Activity Sharing ====================
    
    def share_activity(
        self,
        activity_id: str,
        shared_by: str,
        share_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Share an activity to community"""
        activity = self.db.query(ActivityTemplateDB).filter(
            ActivityTemplateDB.activity_id == activity_id
        ).first()
        
        if not activity:
            raise ValueError(f"Activity {activity_id} not found")
        
        share_id = f"share_{uuid.uuid4().hex[:12]}"
        
        share_info = {
            "share_id": share_id,
            "activity_id": activity_id,
            "shared_by": shared_by,
            "share_type": share_settings.get("share_type", "public"),  # public, org, private
            "org_id": share_settings.get("org_id"),
            "allow_copy": share_settings.get("allow_copy", True),
            "shared_at": utc_now().isoformat(),
            "view_count": 0,
            "copy_count": 0
        }
        
        # Store sharing info (could use a separate table, but for now use tags)
        current_tags = activity.tags or []
        if "shared" not in current_tags:
            current_tags.append("shared")
        activity.tags = current_tags
        
        self.db.commit()
        
        return share_info
    
    def get_shared_activities(
        self,
        org_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get shared activities from community"""
        query = self.db.query(ActivityTemplateDB).filter(
            ActivityTemplateDB.tags.contains(["shared"])
        )
        
        if org_id:
            # Filter by org if needed
            pass
        
        activities = query.order_by(
            desc(ActivityTemplateDB.usage_count)
        ).limit(limit).all()
        
        return [self._template_to_dict(act) for act in activities]
    
    # ==================== Helper Methods ====================
    
    def _template_to_dict(self, template: ActivityTemplateDB) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            "activity_id": template.activity_id,
            "title_ja": template.title_ja,
            "title_zh": template.title_zh,
            "title_en": template.title_en,
            "description_ja": template.description_ja,
            "description_zh": template.description_zh,
            "category": template.category,
            "tags": template.tags or [],
            "difficulty_level": template.difficulty_level,
            "duration_minutes": template.duration_minutes,
            "required_materials": template.required_materials or [],
            "participant_count": template.participant_count,
            "suitable_for": template.suitable_for or [],
            "health_considerations": template.health_considerations or [],
            "steps": template.steps or [],
            "tips": template.tips,
            "variations": template.variations or [],
            "created_by": template.created_by,
            "usage_count": template.usage_count,
            "rating": template.rating,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }
