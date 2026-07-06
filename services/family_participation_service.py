"""
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from models.task_models import TaskDB, ScheduleDB
from models.knowledge_models import FamilyMemberDB
from services.base_service import BaseService
from services.logging_service import logger


class FamilyParticipationService(BaseService):
    """Family participation service"""
    
    def add_family_to_task(
        self,
        task_id: str,
        family_member_id: str
    ) -> Dict[str, Any]:
        """
        Add family member to task
        
        Args:
            task_id: Task ID
            family_member_id: Family member ID
            
        Returns:
            Updated task info
        """
        task = self.db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Validate family member
        family_member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == family_member_id
        ).first()
        
        if not family_member:
            raise ValueError(f"Family member {family_member_id} not found")
        
        # Check permissions
        if not family_member.can_view_tasks:
            raise ValueError(f"Family member {family_member_id} does not have permission to view tasks")
        
        # Validate elder_id match
        if family_member.elder_id != task.elder_id:
            raise ValueError(f"Family member {family_member_id} does not belong to the same elder as task {task_id}")
        
        # Validate org_id match when provided
        if task.org_id and family_member.org_id and task.org_id != family_member.org_id:
            raise ValueError(f"Family member {family_member_id} does not belong to the same organization as task {task_id}")
        
        # Add family member to task
        family_member_ids = task.family_member_ids or []
        if family_member_id not in family_member_ids:
            family_member_ids.append(family_member_id)
            task.family_member_ids = family_member_ids
            task.updated_at = utc_now()
            
            try:
                self.db.commit()
                self.db.refresh(task)
                logger.log_info(f"Family member {family_member_id} added to task {task_id}")
            except Exception as e:
                self.db.rollback()
                logger.log_error(e, {"action": "add_family_to_task", "task_id": task_id, "family_member_id": family_member_id})
                raise ValueError(f"Failed to add family member to task: {str(e)}")
        
        from services.task_service import get_task_service
        task_service = get_task_service(self.db)
        return task_service._task_to_dict(task)
    
    def add_family_to_schedule(
        self,
        schedule_id: str,
        family_member_id: str
    ) -> Dict[str, Any]:
        """
        Add family member to schedule
        
        Args:
            schedule_id: Schedule ID
            family_member_id: Family member ID
            
        Returns:
            Updated schedule info
        """
        schedule = self.db.query(ScheduleDB).filter(ScheduleDB.schedule_id == schedule_id).first()
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        # Validate family member
        family_member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == family_member_id
        ).first()
        
        if not family_member:
            raise ValueError(f"Family member {family_member_id} not found")
        
        # Check permissions
        if not family_member.can_view_schedules:
            raise ValueError(f"Family member {family_member_id} does not have permission to view schedules")
        
        # Validate elder_id match
        if family_member.elder_id != schedule.elder_id:
            raise ValueError(f"Family member {family_member_id} does not belong to the same elder as schedule {schedule_id}")
        
        # Validate org_id match when provided
        if schedule.org_id and family_member.org_id and schedule.org_id != family_member.org_id:
            raise ValueError(f"Family member {family_member_id} does not belong to the same organization as schedule {schedule_id}")
        
        # Add family member to schedule
        participants = schedule.participants or []
        if family_member_id not in participants:
            participants.append(family_member_id)
            schedule.participants = participants
            schedule.updated_at = utc_now()
            
            try:
                self.db.commit()
                self.db.refresh(schedule)
                logger.log_info(f"Family member {family_member_id} added to schedule {schedule_id}")
            except Exception as e:
                self.db.rollback()
                logger.log_error(e, {"action": "add_family_to_schedule", "schedule_id": schedule_id, "family_member_id": family_member_id})
                raise ValueError(f"Failed to add family member to schedule: {str(e)}")
        
        from services.schedule_service import get_schedule_service
        schedule_service = get_schedule_service(self.db)
        return schedule_service._schedule_to_dict(schedule)
    
    def get_family_tasks(
        self,
        family_member_id: str,
        status: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tasks with family member participation
        
        Args:
            family_member_id: Family member ID
            status: Task status (optional)
            org_id: Organization ID (optional, for authorization)
            
        Returns:
            Task list
        """
        # Verify family member exists
        family_member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == family_member_id
        ).first()
        
        if not family_member:
            raise ValueError(f"Family member {family_member_id} not found")
        
        # Validate org_id when provided
        if org_id and family_member.org_id and org_id != family_member.org_id:
            raise ValueError(f"Family member {family_member_id} does not belong to organization {org_id}")
        
        # JSON contains query via SQLAlchemy (parameterized, safe for JSON columns)
        # Note: family_member_ids is a JSON array; contains checks membership
        query = self.db.query(TaskDB).filter(
            TaskDB.family_member_ids.contains([family_member_id])
        )
        
        # Filter by elder_id for performance and security
        query = query.filter(TaskDB.elder_id == family_member.elder_id)
        
        if status:
            query = query.filter(TaskDB.status == status)
        
        tasks = query.order_by(desc(TaskDB.created_at)).all()
        
        from services.task_service import get_task_service
        task_service = get_task_service(self.db)
        return [task_service._task_to_dict(task) for task in tasks]
    
    def get_family_schedules(
        self,
        family_member_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get schedules with family member participation
        
        Args:
            family_member_id: Family member ID
            start_date: Start date (optional)
            end_date: End date (optional)
            org_id: Organization ID (optional, for authorization)
            
        Returns:
            Schedule list
        """
        # Verify family member exists
        family_member = self.db.query(FamilyMemberDB).filter(
            FamilyMemberDB.member_id == family_member_id
        ).first()
        
        if not family_member:
            raise ValueError(f"Family member {family_member_id} not found")
        
        # Validate org_id when provided
        if org_id and family_member.org_id and org_id != family_member.org_id:
            raise ValueError(f"Family member {family_member_id} does not belong to organization {org_id}")
        
        # JSON contains query via SQLAlchemy (safe for JSON columns)
        query = self.db.query(ScheduleDB).filter(
            ScheduleDB.participants.contains([family_member_id])
        )
        
        # Filter by elder_id for performance and security
        query = query.filter(ScheduleDB.elder_id == family_member.elder_id)
        
        if start_date:
            query = query.filter(ScheduleDB.start_time >= start_date)
        if end_date:
            query = query.filter(ScheduleDB.start_time <= end_date)
        
        schedules = query.order_by(ScheduleDB.start_time).all()
        
        from services.schedule_service import get_schedule_service
        schedule_service = get_schedule_service(self.db)
        return [schedule_service._schedule_to_dict(schedule) for schedule in schedules]


def get_family_participation_service(db: Session) -> FamilyParticipationService:
    """Get family participation service instance"""
    return FamilyParticipationService(db)
