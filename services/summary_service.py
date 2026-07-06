"""
Customer Summary Service
Intelligently organizes elder information to avoid repeated questions
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
import json

from models.summary_models import CustomerSummaryDB, InfoChangeLogDB
from models.customer_models import CustomerDB, ElderProfileDB
from services.base_service import BaseService
from services.logging_service import logger


class SummaryService(BaseService):
    """Customer summary service"""
    
    def generate_summary(
        self,
        customer_id: str,
        summary_type: str = "full",
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate customer information summary
        
        Args:
            customer_id: Customer ID
            summary_type: Summary type (full, health, preferences, activities)
            force_regenerate: Whether to force regeneration
            
        Returns:
            Summary data
        """
        # Check for cached summary
        if not force_regenerate:
            cached_summary = self._get_cached_summary(customer_id, summary_type)
            if cached_summary:
                return cached_summary
        
        # Get customer information
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.customer_id == customer_id
        ).first()
        
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get elder profile when customer is an elder
        elder_profile = None
        if customer.customer_type == "elder":
            elder_profile = self.db.query(ElderProfileDB).filter(
                ElderProfileDB.customer_id == customer_id
            ).first()
        
        # Generate summary
        summary_data = self._build_summary_data(customer, elder_profile, summary_type)
        summary_text = self._generate_summary_text(summary_data, summary_type)
        key_info = self._extract_key_info(customer, elder_profile)
        last_updated_fields = self._get_recent_changes(customer_id, days=7)
        
        # Save summary
        summary_id = f"summary_{uuid.uuid4().hex[:12]}"
        summary = CustomerSummaryDB(
            summary_id=summary_id,
            customer_id=customer_id,
            org_id=customer.org_id,
            summary_type=summary_type,
            summary_text=summary_text,
            summary_data=summary_data,
            key_info=key_info,
            last_updated_fields=last_updated_fields,
            expires_at=utc_now() + timedelta(hours=24)  # Expires in 24 hours
        )
        
        self.db.add(summary)
        try:
            self.db.commit()
            self.db.refresh(summary)
        except Exception as e:
            self.db.rollback()
            logger.log_error(e, {"action": "generate_summary", "customer_id": customer_id, "summary_type": summary_type})
            raise ValueError(f"Failed to generate summary: {str(e)}")
        
        return self._summary_to_dict(summary)
    
    def get_info_cards(self, customer_id: str) -> Dict[str, Any]:
        """
        Get information card data (for visualization)
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Information card data
        """
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.customer_id == customer_id
        ).first()
        
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        elder_profile = None
        if customer.customer_type == "elder":
            elder_profile = self.db.query(ElderProfileDB).filter(
                ElderProfileDB.customer_id == customer_id
            ).first()
        
        cards = []
        
        # Basic info card
        cards.append({
            "type": "basic_info",
            "title": "Basic information",
            "data": {
                "name": customer.name,
                "age": customer.age,
                "gender": customer.gender,
                "language": customer.preferred_language
            }
        })
        
        # Health info card
        if elder_profile:
            if elder_profile.health_status or elder_profile.health_conditions:
                cards.append({
                    "type": "health",
                    "title": "Health status",
                    "data": {
                        "health_status": elder_profile.health_status,
                        "health_conditions": elder_profile.health_conditions or [],
                        "mobility_level": elder_profile.mobility_level,
                        "cognitive_level": elder_profile.cognitive_level
                    }
                })
            
            # Emotion pattern card
            if elder_profile.mood_patterns:
                cards.append({
                    "type": "emotions",
                    "title": "Emotion patterns",
                    "data": elder_profile.mood_patterns
                })
            
            # Interests and hobbies card
            if elder_profile.interests or elder_profile.hobbies:
                cards.append({
                    "type": "interests",
                    "title": "Interests and hobbies",
                    "data": {
                        "interests": elder_profile.interests or [],
                        "hobbies": elder_profile.hobbies or []
                    }
                })
        
        # Recent changes card
        recent_changes = self._get_recent_changes(customer_id, days=7)
        if recent_changes:
            cards.append({
                "type": "recent_changes",
                "title": "Recent updates",
                "data": recent_changes
            })
        
        return {
            "customer_id": customer_id,
            "cards": cards,
            "total_cards": len(cards)
        }
    
    def get_info_changes(
        self,
        customer_id: str,
        since: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get information change list
        
        Args:
            customer_id: Customer ID
            since: Since timestamp (optional)
            category: Change category (optional)
            
        Returns:
            Change list
        """
        query = self.db.query(InfoChangeLogDB).filter(
            InfoChangeLogDB.customer_id == customer_id
        )
        
        if since:
            query = query.filter(InfoChangeLogDB.changed_at >= since)
        if category:
            query = query.filter(InfoChangeLogDB.change_category == category)
        
        changes = query.order_by(desc(InfoChangeLogDB.changed_at)).limit(50).all()
        
        return [self._change_to_dict(change) for change in changes]
    
    def log_info_change(
        self,
        customer_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        change_type: str = "updated",
        changed_by: Optional[str] = None,
        change_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record information change
        
        Args:
            customer_id: Customer ID
            field_name: Field name
            old_value: Old value
            new_value: New value
            change_type: Change type (created, updated, deleted)
            changed_by: Changed-by user ID (optional)
            change_category: Change category (optional)
            
        Returns:
            Change record
        """
        change_id = f"change_{uuid.uuid4().hex[:12]}"
        
        # Generate change summary
        change_summary = self._generate_change_summary(field_name, old_value, new_value, change_type)
        
        # Auto-categorize change
        if not change_category:
            change_category = self._categorize_change(field_name)
        
        change = InfoChangeLogDB(
            change_id=change_id,
            customer_id=customer_id,
            change_type=change_type,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            change_summary=change_summary,
            change_category=change_category,
            changed_by=changed_by
        )
        
        self.db.add(change)
        try:
            self.safe_commit("log_info_change")
            self.safe_refresh(change, "log_info_change")
            logger.log_info(f"Info change logged: {change_id} for {customer_id}")
        except Exception as e:
            self.handle_database_error(e, "log_info_change", {"customer_id": customer_id, "change_id": change_id})
            raise
        
        return self._change_to_dict(change)
    
    def _get_cached_summary(self, customer_id: str, summary_type: str) -> Optional[Dict[str, Any]]:
        """Get cached summary"""
        summary = self.db.query(CustomerSummaryDB).filter(
            and_(
                CustomerSummaryDB.customer_id == customer_id,
                CustomerSummaryDB.summary_type == summary_type,
                CustomerSummaryDB.expires_at > utc_now()
            )
        ).order_by(desc(CustomerSummaryDB.generated_at)).first()
        
        if summary:
            return self._summary_to_dict(summary)
        return None
    
    def _build_summary_data(
        self,
        customer: CustomerDB,
        elder_profile: Optional[ElderProfileDB],
        summary_type: str
    ) -> Dict[str, Any]:
        """Build summary payload"""
        data = {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "customer_type": customer.customer_type
        }
        
        if summary_type in ["full", "health"] and elder_profile:
            data["health"] = {
                "health_status": elder_profile.health_status,
                "health_conditions": elder_profile.health_conditions or [],
                "mobility_level": elder_profile.mobility_level,
                "cognitive_level": elder_profile.cognitive_level
            }
        
        if summary_type in ["full", "preferences"] and elder_profile:
            data["preferences"] = {
                "interests": elder_profile.interests or [],
                "hobbies": elder_profile.hobbies or [],
                "favorite_topics": elder_profile.favorite_topics or [],
                "mood_patterns": elder_profile.mood_patterns or {}
            }
        
        if summary_type in ["full", "activities"] and elder_profile:
            data["activities"] = {
                "activity_capabilities": elder_profile.activity_capabilities or [],
                "personality_traits": elder_profile.personality_traits or []
            }
        
        return data
    
    def _generate_summary_text(self, summary_data: Dict[str, Any], summary_type: str) -> str:
        """Generate summaryText"""
        parts = []
        
        parts.append(f"【{summary_data.get('name', 'N/A')}】")
        
        if "health" in summary_data:
            health = summary_data["health"]
            if health.get("health_status"):
                parts.append(f"健康状態: {health['health_status']}")
            if health.get("health_conditions"):
                parts.append(f"健康条件: {', '.join(health['health_conditions'])}")
        
        if "preferences" in summary_data:
            prefs = summary_data["preferences"]
            if prefs.get("interests"):
                parts.append(f"興味: {', '.join(prefs['interests'])}")
            if prefs.get("hobbies"):
                parts.append(f"趣味: {', '.join(prefs['hobbies'])}")
        
        return "\n".join(parts)
    
    def _extract_key_info(
        self,
        customer: CustomerDB,
        elder_profile: Optional[ElderProfileDB]
    ) -> Dict[str, Any]:
        """Extract key information"""
        key_info = {
            "needs": [],
            "emotions": [],
            "health_status": None
        }
        
        if elder_profile:
            # Inferred needs from health and abilities
            if elder_profile.health_conditions:
                key_info["needs"].extend([
                    f"{condition}への対応が必要" for condition in elder_profile.health_conditions
                ])
            
            # Emotion patterns
            if elder_profile.mood_patterns:
                key_info["emotions"] = list(elder_profile.mood_patterns.keys())
            
            # Health status
            key_info["health_status"] = elder_profile.health_status
        
        return key_info
    
    def _get_recent_changes(self, customer_id: str, days: int = 7) -> List[str]:
        """Get recently changed field names"""
        since = utc_now() - timedelta(days=days)
        
        changes = self.db.query(InfoChangeLogDB).filter(
            and_(
                InfoChangeLogDB.customer_id == customer_id,
                InfoChangeLogDB.changed_at >= since
            )
        ).order_by(desc(InfoChangeLogDB.changed_at)).limit(10).all()
        
        return [change.field_name for change in changes]
    
    def _generate_change_summary(
        self,
        field_name: str,
        old_value: Any,
        new_value: Any,
        change_type: str
    ) -> str:
        """Generate change summary"""
        if change_type == "created":
            return f"{field_name}が追加されました"
        elif change_type == "deleted":
            return f"{field_name}が削除されました"
        else:
            return f"{field_name}が更新されました"
    
    def _categorize_change(self, field_name: str) -> str:
        """Auto-categorize change"""
        health_fields = ["health_status", "health_conditions", "mobility_level", "cognitive_level"]
        personal_fields = ["name", "age", "gender", "address"]
        preference_fields = ["interests", "hobbies", "favorite_topics"]
        emotion_fields = ["mood_patterns", "emotion_score"]
        
        if field_name in health_fields:
            return "health"
        elif field_name in personal_fields:
            return "personal"
        elif field_name in preference_fields:
            return "preferences"
        elif field_name in emotion_fields:
            return "emotions"
        else:
            return "other"
    
    def _summary_to_dict(self, summary: CustomerSummaryDB) -> Dict[str, Any]:
        """Convert summary to dict"""
        return {
            "summary_id": summary.summary_id,
            "customer_id": summary.customer_id,
            "org_id": summary.org_id,
            "summary_type": summary.summary_type,
            "summary_text": summary.summary_text,
            "summary_data": summary.summary_data or {},
            "key_info": summary.key_info or {},
            "last_updated_fields": summary.last_updated_fields or [],
            "generated_at": summary.generated_at.isoformat() if summary.generated_at else None,
            "expires_at": summary.expires_at.isoformat() if summary.expires_at else None
        }
    
    def _change_to_dict(self, change: InfoChangeLogDB) -> Dict[str, Any]:
        """Convert change record to dict"""
        return {
            "change_id": change.change_id,
            "customer_id": change.customer_id,
            "change_type": change.change_type,
            "field_name": change.field_name,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "change_summary": change.change_summary,
            "change_category": change.change_category,
            "changed_by": change.changed_by,
            "changed_at": change.changed_at.isoformat() if change.changed_at else None
        }


def get_summary_service(db: Session) -> SummaryService:
    """Get summary service instance"""
    return SummaryService(db)
