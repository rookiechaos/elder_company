"""
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from models.knowledge_models import FamilyMemberDB
from services.base_service import BaseService
from services.logging_service import logger


class FamilyService(BaseService):
    """Family member management service"""
    
    def add_family_member(
        self,
        elder_id: str,
        name: str,
        relationship: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        name_ja: Optional[str] = None,
        name_zh: Optional[str] = None,
        notification_preferences: Optional[Dict[str, bool]] = None,
        can_view_tasks: bool = True,
        can_view_schedules: bool = True,
        can_view_emotions: bool = False,
        can_view_activities: bool = True,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add family member
        
        Args:
            elder_id: Elder ID
            name: Name
            relationship: Relationship (son, daughter, spouse, etc.)
            phone: Phone (optional)
            email: Email (optional)
            name_ja: Japanese name (optional)
            name_zh: Chinese name (optional)
            notification_preferences: Notification preferences (optional)
            can_view_tasks: Can view tasks (default True)
            can_view_schedules: Can view schedules (default True)
            can_view_emotions: Can view emotions (default False)
            can_view_activities: Can view activities (default True)
            org_id: Organization ID (optional)
            
        Returns:
            Created family member info
        """
        member_id = f"family_{uuid.uuid4().hex[:12]}"
        
        # Default notification preferences
        if notification_preferences is None:
            notification_preferences = {
                "tasks": True,
                "schedules": True,
                "emergency": True,
                "activities": True
            }
        
        member = FamilyMemberDB(
            member_id=member_id,
            elder_id=elder_id,
            org_id=org_id,
            name=name,
            name_ja=name_ja,
            name_zh=name_zh,
            relationship=relationship,
            phone=phone,
            email=email,
            notification_preferences=notification_preferences,
            can_view_tasks=can_view_tasks,
            can_view_schedules=can_view_schedules,
            can_view_emotions=can_view_emotions,
            can_view_activities=can_view_activities
        )
        
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        
        logger.log_info(f"Family member added: {member_id}")
        
        return self._member_to_dict(member)
    
    def get_family_members(
        self,
        elder_id: str,
        org_id: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get family member list
        
        Args:
            elder_id: Elder ID
            org_id: Organization ID (optional)
            is_active: Active flag (optional)
            
        Returns:
            Family member list
        """
        query = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.elder_id == elder_id
        )
        
        if org_id:
            query = query.filter(FamilyMemberDB.org_id == org_id)
        if is_active is not None:
            query = query.filter(FamilyMemberDB.is_active == is_active)
        
        members = query.order_by(desc(FamilyMemberDB.created_at)).all()
        
        return [self._member_to_dict(member) for member in members]
    
    def get_family_member(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get a single family member"""
        member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == member_id
        ).first()
        
        if not member:
            return None
        
        return self._member_to_dict(member)
    
    def update_family_member(
        self,
        member_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        notification_preferences: Optional[Dict[str, bool]] = None,
        can_view_tasks: Optional[bool] = None,
        can_view_schedules: Optional[bool] = None,
        can_view_emotions: Optional[bool] = None,
        can_view_activities: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update family member information
        
        Args:
            member_id: Family member ID
            name: Name (optional)
            phone: Phone (optional)
            email: Email (optional)
            notification_preferences: Notification preferences (optional)
            can_view_tasks: Can view tasks (optional)
            can_view_schedules: Can view schedules (optional)
            can_view_emotions: Can view emotions (optional)
            can_view_activities: Can view activities (optional)
            is_active: Active flag (optional)
            
        Returns:
            Updated family member info
        """
        member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == member_id
        ).first()
        
        if not member:
            raise ValueError(f"Family member {member_id} not found")
        
        if name is not None:
            member.name = name
        if phone is not None:
            member.phone = phone
        if email is not None:
            member.email = email
        if notification_preferences is not None:
            member.notification_preferences = notification_preferences
        if can_view_tasks is not None:
            member.can_view_tasks = can_view_tasks
        if can_view_schedules is not None:
            member.can_view_schedules = can_view_schedules
        if can_view_emotions is not None:
            member.can_view_emotions = can_view_emotions
        if can_view_activities is not None:
            member.can_view_activities = can_view_activities
        if is_active is not None:
            member.is_active = is_active
        
        member.updated_at = utc_now()
        
        self.db.commit()
        self.db.refresh(member)
        
        return self._member_to_dict(member)
    
    def delete_family_member(self, member_id: str) -> bool:
        """
        Delete family member
        
        Args:
            member_id: Family member ID
            
        Returns:
            Whether delete succeeded
        """
        member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == member_id
        ).first()
        
        if not member:
            return False
        
        self.db.delete(member)
        self.db.commit()
        
        logger.log_info(f"Family member deleted: {member_id}")
        return True
    
    def _member_to_dict(self, member: FamilyMemberDB) -> Dict[str, Any]:
        """Convert family member to dict"""
        return {
            "member_id": member.member_id,
            "elder_id": member.elder_id,
            "org_id": member.org_id,
            "name": member.name,
            "name_ja": member.name_ja,
            "name_zh": member.name_zh,
            "relationship": member.relationship,
            "phone": member.phone,
            "email": member.email,
            "notification_preferences": member.notification_preferences or {},
            "can_view_tasks": member.can_view_tasks,
            "can_view_schedules": member.can_view_schedules,
            "can_view_emotions": member.can_view_emotions,
            "can_view_activities": member.can_view_activities,
            "is_active": member.is_active,
            "is_verified": member.is_verified,
            "created_at": member.created_at.isoformat() if member.created_at else None,
            "updated_at": member.updated_at.isoformat() if member.updated_at else None
        }


def get_family_service(db: Session) -> FamilyService:
    """Get family service instance"""
    return FamilyService(db)
