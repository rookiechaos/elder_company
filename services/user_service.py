"""
User Service - Manages user profiles and personalization
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from models.database import UserProfileDB, TranslationHistoryDB
from config.database import get_db
from services.base_service import BaseService


class UserService(BaseService):
    """Service for managing user profiles and personalization"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        profile = self.db.query(UserProfileDB).filter(
            UserProfileDB.user_id == user_id
        ).first()
        
        if not profile:
            # Return default profile
            return self._get_default_profile(user_id)
        
        return self._profile_to_dict(profile)
    
    def update_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update or create user profile"""
        profile = self.db.query(UserProfileDB).filter(
            UserProfileDB.user_id == user_id
        ).first()
        
        if profile:
            # Update existing profile
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.updated_at = utc_now()
        else:
            # Create new profile
            profile = UserProfileDB(
                user_id=user_id,
                **profile_data
            )
            self.db.add(profile)
        
        try:
            self.safe_commit("update_user_profile")
            self.safe_refresh(profile, "update_user_profile")
        except Exception as e:
            self.handle_database_error(e, "update_user_profile", {"user_id": user_id})
            raise
        
        return self._profile_to_dict(profile)
    
    def get_personalization_context(
        self,
        user_id: str,
        org_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get personalization context for translation"""
        profile = self.get_user_profile(user_id)
        
        # Merge user and organization settings
        custom_terms = profile.get("custom_terms", {}).copy()
        care_scenarios = profile.get("care_scenarios", []).copy()
        
        if org_context:
            # Merge org-level custom terms
            org_terms = org_context.get("org_custom_terms", {})
            custom_terms.update(org_terms)
            
            # Merge org-level care scenarios
            org_scenarios = org_context.get("org_care_scenarios", [])
            care_scenarios.extend(org_scenarios)
            care_scenarios = list(set(care_scenarios))  # Deduplicate
        
        context = {
            "translation_style": profile.get("translation_style", "professional"),
            "detail_level": profile.get("detail_level", "moderate"),
            "use_honorifics": profile.get("use_honorifics", True),
            "care_scenarios": care_scenarios,
            "custom_terms": custom_terms,
            "role": profile.get("role"),
            "experience_years": profile.get("experience_years"),
        }
        
        return context
    
    def save_translation_history(
        self,
        user_id: str,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None,
        org_id: Optional[str] = None,
        text_length: Optional[int] = None,
        translation_time_ms: Optional[int] = None,
        provider: Optional[str] = None
    ):
        """Save translation to history"""
        history = TranslationHistoryDB(
            user_id=user_id,
            org_id=org_id,
            original_text=original_text,
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            context=context,
            text_length=text_length or len(original_text),
            translation_time_ms=translation_time_ms,
            provider=provider
        )
        self.db.add(history)
        self.db.commit()
    
    def get_translation_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> list:
        """Get user's translation history"""
        history = self.db.query(TranslationHistoryDB).filter(
            TranslationHistoryDB.user_id == user_id
        ).order_by(TranslationHistoryDB.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "id": h.id,
                "original_text": h.original_text,
                "translated_text": h.translated_text,
                "source_language": h.source_language,
                "target_language": h.target_language,
                "context": h.context,
                "timestamp": h.timestamp.isoformat()
            }
            for h in history
        ]
    
    def _profile_to_dict(self, profile: UserProfileDB) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "user_id": profile.user_id,
            "org_id": profile.org_id,
            "name": profile.name,
            "name_ja": profile.name_ja,
            "role": profile.role,
            "experience_years": profile.experience_years,
            "user_role": profile.user_role,
            "is_active": profile.is_active,
            "preferred_source_language": profile.preferred_source_language,
            "preferred_target_language": profile.preferred_target_language,
            "translation_style": profile.translation_style,
            "detail_level": profile.detail_level,
            "use_honorifics": profile.use_honorifics,
            "care_scenarios": profile.care_scenarios or [],
            "custom_terms": profile.custom_terms or {},
            "work_shift": profile.work_shift,
            "common_tasks": profile.common_tasks or [],
            "preferences": profile.preferences or {},
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }
    
    def _get_default_profile(self, user_id: str) -> Dict[str, Any]:
        """Get default profile"""
        return {
            "user_id": user_id,
            "name": None,
            "role": None,
            "experience_years": None,
            "preferred_source_language": "ja",
            "preferred_target_language": "zh",
            "translation_style": "professional",
            "detail_level": "moderate",
            "use_honorifics": True,
            "care_scenarios": [],
            "custom_terms": {},
            "work_shift": None,
            "common_tasks": [],
            "preferences": {},
            "created_at": None,
            "updated_at": None,
        }
