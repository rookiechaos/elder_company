"""
Schedule Management Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import uuid
import json

from models.task_models import ScheduleDB
from services.base_service import BaseService
from services.logging_service import logger


class ScheduleService(BaseService):
    """Schedule management service"""
    
    def create_schedule(
        self,
        caregiver_id: str,
        elder_id: str,
        title: str,
        schedule_type: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        recurrence: str = "none",
        recurrence_end_date: Optional[datetime] = None,
        recurrence_pattern: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        participants: Optional[List[str]] = None,
        is_shared: bool = True,
        shared_with: Optional[List[str]] = None,
        reminders: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        location: Optional[str] = None,
        org_id: Optional[str] = None,
        relationship_id: Optional[str] = None,
        related_task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create schedule
        
        Args:
            caregiver_id: Caregiver ID
            elder_id: Elder ID
            title: Schedule title
            schedule_type: Schedule type (medication, exercise, appointment, activity)
            start_time: Start time
            end_time: End time (optional)
            recurrence: Recurrence (daily, weekly, monthly, custom, none)
            recurrence_end_date: Recurrence end date (optional)
            recurrence_pattern: Custom recurrence pattern (optional)
            description: Description (optional)
            participants: Participant ID list (optional)
            is_shared: Shared flag (default True)
            shared_with: Family member IDs to share with (optional)
            reminders: Reminder settings list (optional)
            notes: Notes (optional)
            location: Location (optional)
            org_id: Organization ID (optional)
            relationship_id: Relationship ID (optional)
            related_task_id: Related task ID (optional)
            
        Returns:
            Created schedule info
        """
        schedule_id = f"schedule_{uuid.uuid4().hex[:12]}"
        
        # Ensure participants include caregiver and elder
        if participants is None:
            participants = []
        if caregiver_id not in participants:
            participants.append(caregiver_id)
        if elder_id not in participants:
            participants.append(elder_id)
        
        schedule = ScheduleDB(
            schedule_id=schedule_id,
            title=title,
            description=description,
            schedule_type=schedule_type,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            relationship_id=relationship_id,
            start_time=start_time,
            end_time=end_time,
            recurrence=recurrence,
            recurrence_end_date=recurrence_end_date,
            recurrence_pattern=recurrence_pattern,
            participants=participants,
            is_shared=is_shared,
            shared_with=shared_with or [],
            reminders=reminders or [],
            notes=notes,
            location=location,
            related_task_id=related_task_id
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.log_info(
            f"Schedule created: {schedule_id}",
            {"schedule_id": schedule_id, "caregiver_id": caregiver_id, "elder_id": elder_id, "schedule_type": schedule_type}
        )
        
        return self._schedule_to_dict(schedule)
    
    def get_schedules(
        self,
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        schedule_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        org_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get schedule list
        
        Args:
            caregiver_id: Caregiver ID (optional)
            elder_id: Elder ID (optional)
            schedule_type: Schedule type (optional)
            start_date: Start date (optional)
            end_date: End date (optional)
            org_id: Organization ID (optional)
            limit: Result limit
            
        Returns:
            Schedule list
        """
        query = self.db.query(ScheduleDB)
        
        if caregiver_id:
            query = query.filter(ScheduleDB.caregiver_id == caregiver_id)
        if elder_id:
            query = query.filter(ScheduleDB.elder_id == elder_id)
        if schedule_type:
            query = query.filter(ScheduleDB.schedule_type == schedule_type)
        if org_id:
            query = query.filter(ScheduleDB.org_id == org_id)
        if start_date:
            query = query.filter(ScheduleDB.start_time >= start_date)
        if end_date:
            query = query.filter(ScheduleDB.start_time <= end_date)
        
        schedules = query.order_by(ScheduleDB.start_time).limit(limit).all()
        
        return [self._schedule_to_dict(schedule) for schedule in schedules]
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Get a single schedule"""
        schedule = self.db.query(ScheduleDB).filter(ScheduleDB.schedule_id == schedule_id).first()
        if not schedule:
            return None
        return self._schedule_to_dict(schedule)
    
    def get_calendar_view(
        self,
        elder_id: str,
        start_date: datetime,
        end_date: datetime,
        caregiver_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get calendar view data
        
        Args:
            elder_id: Elder ID
            start_date: Start date
            end_date: End date
            caregiver_id: Caregiver ID (optional)
            
        Returns:
            Calendar view data (grouped by date)
        """
        query = self.db.query(ScheduleDB).filter(
            and_(
                ScheduleDB.elder_id == elder_id,
                ScheduleDB.start_time >= start_date,
                ScheduleDB.start_time <= end_date
            )
        )
        
        if caregiver_id:
            query = query.filter(ScheduleDB.caregiver_id == caregiver_id)
        
        schedules = query.order_by(ScheduleDB.start_time).all()
        
        # Group by date
        calendar_data = {}
        for schedule in schedules:
            date_key = schedule.start_time.date().isoformat()
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(self._schedule_to_dict(schedule))
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "schedules_by_date": calendar_data,
            "total_schedules": len(schedules)
        }
    
    def update_schedule(
        self,
        schedule_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        recurrence: Optional[str] = None,
        participants: Optional[List[str]] = None,
        is_shared: Optional[bool] = None,
        reminders: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update schedule
        
        Args:
            schedule_id: Schedule ID
            title: Title (optional)
            description: Description (optional)
            start_time: Start time (optional)
            end_time: End time (optional)
            recurrence: Recurrence (optional)
            participants: Participants (optional)
            is_shared: Shared flag (optional)
            reminders: Reminder settings (optional)
            notes: Notes (optional)
            location: Location (optional)
            
        Returns:
            Updated schedule info
        """
        schedule = self.db.query(ScheduleDB).filter(ScheduleDB.schedule_id == schedule_id).first()
        if not schedule:
            raise ValueError(f"Schedule {schedule_id} not found")
        
        if title is not None:
            schedule.title = title
        if description is not None:
            schedule.description = description
        if start_time is not None:
            schedule.start_time = start_time
        if end_time is not None:
            schedule.end_time = end_time
        if recurrence is not None:
            schedule.recurrence = recurrence
        if participants is not None:
            schedule.participants = participants
        if is_shared is not None:
            schedule.is_shared = is_shared
        if reminders is not None:
            schedule.reminders = reminders
        if notes is not None:
            schedule.notes = notes
        if location is not None:
            schedule.location = location
        
        schedule.updated_at = utc_now()
        
        self.db.commit()
        self.db.refresh(schedule)
        
        return self._schedule_to_dict(schedule)
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete schedule
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Whether delete succeeded
        """
        schedule = self.db.query(ScheduleDB).filter(ScheduleDB.schedule_id == schedule_id).first()
        if not schedule:
            return False
        
        self.db.delete(schedule)
        self.db.commit()
        
        logger.log_info(f"Schedule deleted: {schedule_id}")
        return True
    
    def _schedule_to_dict(self, schedule: ScheduleDB) -> Dict[str, Any]:
        """Convert schedule to dict"""
        return {
            "schedule_id": schedule.schedule_id,
            "title": schedule.title,
            "description": schedule.description,
            "schedule_type": schedule.schedule_type,
            "caregiver_id": schedule.caregiver_id,
            "elder_id": schedule.elder_id,
            "org_id": schedule.org_id,
            "relationship_id": schedule.relationship_id,
            "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
            "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
            "recurrence": schedule.recurrence,
            "recurrence_end_date": schedule.recurrence_end_date.isoformat() if schedule.recurrence_end_date else None,
            "recurrence_pattern": schedule.recurrence_pattern,
            "participants": schedule.participants or [],
            "is_shared": schedule.is_shared,
            "shared_with": schedule.shared_with or [],
            "reminders": schedule.reminders or [],
            "notes": schedule.notes,
            "location": schedule.location,
            "related_task_id": schedule.related_task_id,
            "created_at": schedule.created_at.isoformat() if schedule.created_at else None,
            "updated_at": schedule.updated_at.isoformat() if schedule.updated_at else None,
            "extra_metadata": schedule.extra_metadata
        }


def get_schedule_service(db: Session) -> ScheduleService:
    """Get schedule service instance"""
    return ScheduleService(db)
