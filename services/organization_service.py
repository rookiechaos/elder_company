"""
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models.database import (
    OrganizationDB, UserProfileDB, TranslationHistoryDB, UsageStatisticsDB
)
from services.cache_service import get_cache, CACHE_TTL


class OrganizationService:
    """Service for managing organizations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_organization(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new organization"""
        org = OrganizationDB(**org_data)
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return self._org_to_dict(org)
    
    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID with caching"""
        cache = get_cache()
        cache_key = f"organization:info:{org_id}"
        
        # Try cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        org = self.db.query(OrganizationDB).filter(
            OrganizationDB.org_id == org_id
        ).first()
        
        if not org:
            return None
        
        result = self._org_to_dict(org)
        
        # Cache result
        cache.set(cache_key, result, CACHE_TTL["organization"])
        
        return result
    
    def update_organization(
        self,
        org_id: str,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update organization"""
        org = self.db.query(OrganizationDB).filter(
            OrganizationDB.org_id == org_id
        ).first()
        
        if not org:
            raise ValueError(f"Organization {org_id} not found")
        
        for key, value in update_data.items():
            if hasattr(org, key):
                setattr(org, key, value)
        
        org.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(org)
        
        result = self._org_to_dict(org)
        
        # Invalidate cache
        cache = get_cache()
        cache.delete(f"organization:info:{org_id}")
        
        return result
    
    def get_organization_users(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all users in an organization"""
        users = self.db.query(UserProfileDB).filter(
            UserProfileDB.org_id == org_id
        ).all()
        
        return [
            {
                "user_id": u.user_id,
                "name": u.name,
                "name_ja": u.name_ja,
                "role": u.role,
                "user_role": u.user_role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    
    def get_organization_statistics(
        self,
        org_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get organization usage statistics"""
        start_date = utc_now() - timedelta(days=days)
        
        # Total translation count
        total_translations = self.db.query(func.count(TranslationHistoryDB.id)).filter(
            and_(
                TranslationHistoryDB.org_id == org_id,
                TranslationHistoryDB.timestamp >= start_date
            )
        ).scalar() or 0
        
        # Active user count
        active_users = self.db.query(func.count(func.distinct(TranslationHistoryDB.user_id))).filter(
            and_(
                TranslationHistoryDB.org_id == org_id,
                TranslationHistoryDB.timestamp >= start_date
            )
        ).scalar() or 0
        
        # Language-pair statistics
        language_pairs = {}
        translations = self.db.query(TranslationHistoryDB).filter(
            and_(
                TranslationHistoryDB.org_id == org_id,
                TranslationHistoryDB.timestamp >= start_date
            )
        ).all()
        
        for t in translations:
            pair = f"{t.source_language}-{t.target_language}"
            language_pairs[pair] = language_pairs.get(pair, 0) + 1
        
        # Daily statistics
        daily_stats = self.db.query(UsageStatisticsDB).filter(
            and_(
                UsageStatisticsDB.org_id == org_id,
                UsageStatisticsDB.date >= start_date.strftime("%Y-%m-%d")
            )
        ).order_by(UsageStatisticsDB.date.desc()).limit(days).all()
        
        daily_data = [
            {
                "date": stat.date,
                "translation_count": stat.translation_count,
                "total_characters": stat.total_characters
            }
            for stat in daily_stats
        ]
        
        return {
            "org_id": org_id,
            "period_days": days,
            "total_translations": total_translations,
            "active_users": active_users,
            "language_pairs": language_pairs,
            "daily_statistics": daily_data
        }
    
    def check_translation_limit(self, org_id: str) -> Tuple[bool, Optional[str]]:
        """Check if organization has reached translation limit"""
        org = self.db.query(OrganizationDB).filter(
            OrganizationDB.org_id == org_id
        ).first()
        
        if not org:
            return False, "Organization not found"
        
        if not org.is_active:
            return False, "Organization is inactive"
        
        # Check monthly translation count
        start_of_month = utc_now().replace(day=1, hour=0, minute=0, second=0)
        monthly_count = self.db.query(func.count(TranslationHistoryDB.id)).filter(
            and_(
                TranslationHistoryDB.org_id == org_id,
                TranslationHistoryDB.timestamp >= start_of_month
            )
        ).scalar() or 0
        
        if monthly_count >= org.monthly_translation_limit:
            return False, f"Monthly translation limit ({org.monthly_translation_limit}) reached"
        
        return True, None
    
    def record_translation(
        self,
        org_id: str,
        user_id: str,
        text_length: int,
        translation_time_ms: int,
        source_language: str,
        target_language: str
    ):
        """Record a translation for statistics"""
        # Update org total translation count
        org = self.db.query(OrganizationDB).filter(
            OrganizationDB.org_id == org_id
        ).first()
        if org:
            org.total_translations += 1
            self.db.commit()
        
        # Update daily statistics
        today = utc_now().strftime("%Y-%m-%d")
        stat = self.db.query(UsageStatisticsDB).filter(
            and_(
                UsageStatisticsDB.org_id == org_id,
                UsageStatisticsDB.date == today
            )
        ).first()
        
        if stat:
            stat.translation_count += 1
            stat.total_characters += text_length
            if stat.language_pairs:
                pair = f"{source_language}-{target_language}"
                stat.language_pairs[pair] = stat.language_pairs.get(pair, 0) + 1
            else:
                stat.language_pairs = {f"{source_language}-{target_language}": 1}
        else:
            stat = UsageStatisticsDB(
                org_id=org_id,
                user_id=user_id,
                date=today,
                translation_count=1,
                total_characters=text_length,
                language_pairs={f"{source_language}-{target_language}": 1}
            )
            self.db.add(stat)
        
        self.db.commit()
    
    def _org_to_dict(self, org: OrganizationDB) -> Dict[str, Any]:
        """Convert organization to dictionary"""
        return {
            "org_id": org.org_id,
            "name": org.name,
            "name_ja": org.name_ja,
            "org_type": org.org_type,
            "address": org.address,
            "phone": org.phone,
            "email": org.email,
            "default_source_language": org.default_source_language,
            "default_target_language": org.default_target_language,
            "org_custom_terms": org.org_custom_terms or {},
            "org_care_scenarios": org.org_care_scenarios or [],
            "subscription_plan": org.subscription_plan,
            "max_users": org.max_users,
            "monthly_translation_limit": org.monthly_translation_limit,
            "total_translations": org.total_translations,
            "active_users_count": org.active_users_count,
            "is_active": org.is_active,
            "created_at": org.created_at.isoformat() if org.created_at else None,
            "updated_at": org.updated_at.isoformat() if org.updated_at else None,
        }
