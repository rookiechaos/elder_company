"""
Task Management Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import uuid
import json

from models.task_models import TaskDB
from services.base_service import BaseService
from services.logging_service import logger


class TaskService(BaseService):
    """Task management service"""
    
    def create_task(
        self,
        caregiver_id: str,
        elder_id: str,
        title: str,
        task_type: str,
        due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        priority: str = "medium",
        family_member_ids: Optional[List[str]] = None,
        reminders: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        org_id: Optional[str] = None,
        relationship_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create task
        
        Args:
            caregiver_id: Caregiver ID
            elder_id: Elder ID
            title: Task title
            task_type: Task type (medication, exercise, appointment, custom)
            due_date: Due datetime
            description: Task description
            priority: Priority (low, medium, high)
            family_member_ids: Family member ID list
            reminders: Reminder settings list
            notes: Notes
            org_id: Organization ID
            relationship_id: Relationship ID
            
        Returns:
            Created task info
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        task = TaskDB(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            org_id=org_id,
            relationship_id=relationship_id,
            family_member_ids=family_member_ids or [],
            status="pending",
            priority=priority,
            due_date=due_date,
            reminders=reminders or [],
            notes=notes,
            progress=0
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.log_info(
            f"Task created: {task_id}",
            {"task_id": task_id, "caregiver_id": caregiver_id, "elder_id": elder_id, "task_type": task_type}
        )
        
        return self._task_to_dict(task)
    
    def get_tasks(
        self,
        caregiver_id: Optional[str] = None,
        elder_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        org_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get task list
        
        Args:
            caregiver_id: Caregiver ID (optional)
            elder_id: Elder ID (optional)
            status: Task status (optional)
            task_type: Task type (optional)
            start_date: Start date (optional)
            end_date: End date (optional)
            org_id: Organization ID (optional)
            limit: Result limit
            
        Returns:
            Task list
        """
        query = self.db.query(TaskDB)
        
        if caregiver_id:
            query = query.filter(TaskDB.caregiver_id == caregiver_id)
        if elder_id:
            query = query.filter(TaskDB.elder_id == elder_id)
        if status:
            query = query.filter(TaskDB.status == status)
        if task_type:
            query = query.filter(TaskDB.task_type == task_type)
        if org_id:
            query = query.filter(TaskDB.org_id == org_id)
        if start_date:
            query = query.filter(TaskDB.due_date >= start_date)
        if end_date:
            query = query.filter(TaskDB.due_date <= end_date)
        
        tasks = query.order_by(desc(TaskDB.created_at)).limit(limit).all()
        
        return [self._task_to_dict(task) for task in tasks]
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a single task"""
        task = self.db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
        if not task:
            return None
        return self._task_to_dict(task)
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        reminders: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Update task
        
        Args:
            task_id: Task ID
            title: Task title (optional)
            description: Task description (optional)
            status: Task status (optional)
            progress: Progress (0-100, optional)
            priority: Priority (optional)
            due_date: Due time (optional)
            notes: Notes (optional)
            reminders: Reminder settings (optional)
            
        Returns:
            Updated task info
        """
        task = self.db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
            if status == "completed":
                task.completed_at = utc_now()
        if progress is not None:
            task.progress = max(0, min(100, progress))  # Clamp to 0-100
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        if notes is not None:
            task.notes = notes
        if reminders is not None:
            task.reminders = reminders
        
        task.updated_at = utc_now()
        
        self.db.commit()
        self.db.refresh(task)
        
        return self._task_to_dict(task)
    
    def complete_task(
        self,
        task_id: str,
        completed_by: str,
        completion_notes: Optional[str] = None,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Complete task
        
        Args:
            task_id: Task ID
            completed_by: Completed-by user ID
            completion_notes: Completion notes (optional)
            generate_summary: Generate AI summary (optional)
            
        Returns:
            Completed task info
        """
        task = self.db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.status = "completed"
        task.progress = 100
        task.completed_at = utc_now()
        task.completed_by = completed_by
        task.completion_notes = completion_notes
        
        # Generate AI summary if enabled
        if generate_summary:
            try:
                summary = self._generate_completion_summary(task)
                task.completion_summary = summary
            except Exception as e:
                logger.log_warning(f"Failed to generate task summary: {e}")
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.log_info(
            f"Task completed: {task_id}",
            {"task_id": task_id, "completed_by": completed_by}
        )
        
        return self._task_to_dict(task)
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Get task progress visualization data
        
        Args:
            task_id: Task ID
            
        Returns:
            Progress data
        """
        task = self.db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        return {
            "task_id": task_id,
            "title": task.title,
            "status": task.status,
            "progress": task.progress,
            "progress_percentage": task.progress,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "time_remaining": self._calculate_time_remaining(task),
            "is_overdue": self._is_overdue(task)
        }
    
    def get_daily_summary(
        self,
        elder_id: str,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get daily task completion summary
        
        Args:
            elder_id: Elder ID
            date: Date (defaults to today)
            
        Returns:
            Daily summary (gentle, encouraging tone)
        """
        if date is None:
            date = utc_now()
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        tasks = self.db.query(TaskDB).filter(
            and_(
                TaskDB.elder_id == elder_id,
                TaskDB.created_at >= start_of_day,
                TaskDB.created_at <= end_of_day
            )
        ).all()
        
        completed_tasks = [t for t in tasks if t.status == "completed"]
        pending_tasks = [t for t in tasks if t.status == "pending"]
        in_progress_tasks = [t for t in tasks if t.status == "in_progress"]
        
        # Generate gentle summary text
        summary_text = self._generate_daily_summary_text(
            completed_tasks,
            pending_tasks,
            in_progress_tasks,
            date
        )
        
        return {
            "date": date.isoformat(),
            "total_tasks": len(tasks),
            "completed_count": len(completed_tasks),
            "pending_count": len(pending_tasks),
            "in_progress_count": len(in_progress_tasks),
            "completed_tasks": [self._task_to_dict(t) for t in completed_tasks],
            "pending_tasks": [self._task_to_dict(t) for t in pending_tasks],
            "in_progress_tasks": [self._task_to_dict(t) for t in in_progress_tasks],
            "summary_text": summary_text
        }
    
    def _task_to_dict(self, task: TaskDB) -> Dict[str, Any]:
        """Convert task to dict"""
        return {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type,
            "caregiver_id": task.caregiver_id,
            "elder_id": task.elder_id,
            "org_id": task.org_id,
            "relationship_id": task.relationship_id,
            "family_member_ids": task.family_member_ids or [],
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "progress": task.progress,
            "progress_notes": task.progress_notes,
            "reminders": task.reminders or [],
            "notes": task.notes,
            "completed_by": task.completed_by,
            "completion_notes": task.completion_notes,
            "completion_summary": task.completion_summary,
            "extra_metadata": task.extra_metadata
        }
    
    def _calculate_time_remaining(self, task: TaskDB) -> Optional[int]:
        """Compute remaining time (seconds)"""
        if not task.due_date:
            return None
        if task.status == "completed":
            return 0
        
        now = utc_now()
        if task.due_date > now:
            return int((task.due_date - now).total_seconds())
        return 0
    
    def _is_overdue(self, task: TaskDB) -> bool:
        """Check whether task is overdue"""
        if task.status == "completed":
            return False
        if not task.due_date:
            return False
        return utc_now() > task.due_date
    
    def _generate_completion_summary(self, task: TaskDB) -> str:
        """
        Generate task completion summary (AI)
        
        Args:
            task: Task object
            
        Returns:
            Completion summary text
        """
        # TODO: Integrate AI summary generation
        # Return simple summary for now
        return f"Task \"{task.title}\" has been completed."
    
    def _generate_daily_summary_text(
        self,
        completed_tasks: List[TaskDB],
        pending_tasks: List[TaskDB],
        in_progress_tasks: List[TaskDB],
        date: datetime
    ) -> str:
        """
        Generate daily summary text (gentle, encouraging tone)
        
        Args:
            completed_tasks: Completed task list
            pending_tasks: Pending task list
            in_progress_tasks: In-progress task list
            date: Date
            
        Returns:
            Summary text
        """
        # Base summary
        if len(completed_tasks) == 0:
            return "今日は新しい一日の始まりです。一緒に頑張りましょう。"
        
        completed_titles = [t.title for t in completed_tasks[:3]]  # Show at most 3
        
        if len(completed_tasks) == 1:
            return f"素晴らしい！今日は「{completed_titles[0]}」を一緒に完了しました。"
        elif len(completed_tasks) <= 3:
            tasks_str = "、".join([f"「{t}」" for t in completed_titles])
            return f"今日は素晴らしい一日でした。{tasks_str}を一緒に完了しました！"
        else:
            return f"今日は素晴らしい一日でした。{len(completed_tasks)}つのタスクを一緒に完了しました！"
        
        # TODO: Use AI for more personalized summary


def get_task_service(db: Session) -> TaskService:
    """Get task service instance"""
    return TaskService(db)
