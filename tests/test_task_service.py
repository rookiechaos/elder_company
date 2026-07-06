"""
Task Service Unit Tests
"""

import pytest
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session

from services.task_service import TaskService, get_task_service
from models.task_models import TaskDB
from config.database import SessionLocal, init_database


@pytest.fixture
def db_session():
    """Create test database session"""
    init_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def task_service(db_session):
    """Create task service instance"""
    return get_task_service(db_session)


@pytest.fixture
def sample_caregiver_id():
    """Sample caregiver ID"""
    return "caregiver_test_123"


@pytest.fixture
def sample_elder_id():
    """Sample elder ID"""
    return "elder_test_456"


class TestTaskService:
    """Task service test class"""
    
    def test_create_task(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test create task"""
        task = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test task",
            task_type="medication",
            due_date=utc_now() + timedelta(hours=1)
        )
        
        assert task is not None
        assert task["title"] == "Test task"
        assert task["task_type"] == "medication"
        assert task["status"] == "pending"
        assert task["progress"] == 0
        assert "task_id" in task
    
    def test_get_task(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test get task"""
        # Create task
        created_task = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test task",
            task_type="medication"
        )
        
        # Get task
        task = task_service.get_task(created_task["task_id"])
        
        assert task is not None
        assert task["task_id"] == created_task["task_id"]
        assert task["title"] == "Test task"
    
    def test_get_tasks(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test get task list"""
        # Create multiple tasks
        task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Task 1",
            task_type="medication"
        )
        task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Task 2",
            task_type="exercise"
        )
        
        # Get task list
        tasks = task_service.get_tasks(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id
        )
        
        assert len(tasks) >= 2
        assert any(t["title"] == "Task 1" for t in tasks)
        assert any(t["title"] == "Task 2" for t in tasks)
    
    def test_update_task(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test update task"""
        # Create task
        created_task = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test task",
            task_type="medication"
        )
        
        # Update task
        updated_task = task_service.update_task(
            task_id=created_task["task_id"],
            status="in_progress",
            progress=50
        )
        
        assert updated_task["status"] == "in_progress"
        assert updated_task["progress"] == 50
    
    def test_complete_task(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test complete task"""
        # Create task
        created_task = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test task",
            task_type="medication"
        )
        
        # Complete task
        completed_task = task_service.complete_task(
            task_id=created_task["task_id"],
            completed_by=sample_caregiver_id
        )
        
        assert completed_task["status"] == "completed"
        assert completed_task["progress"] == 100
        assert completed_task["completed_at"] is not None
        assert completed_task["completed_by"] == sample_caregiver_id
    
    def test_get_task_progress(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test get task progress"""
        # Create task
        created_task = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test task",
            task_type="medication",
            due_date=utc_now() + timedelta(hours=1)
        )
        
        # Get progress
        progress = task_service.get_task_progress(created_task["task_id"])
        
        assert progress is not None
        assert progress["task_id"] == created_task["task_id"]
        assert progress["progress"] == 0
        assert "time_remaining" in progress
        assert "is_overdue" in progress
    
    def test_get_daily_summary(self, task_service, sample_caregiver_id, sample_elder_id):
        """Test get daily summary"""
        # Create task
        task1 = task_service.create_task(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Task 1",
            task_type="medication"
        )
        
        # Complete task
        task_service.complete_task(
            task_id=task1["task_id"],
            completed_by=sample_caregiver_id
        )
        
        # Get daily summary
        summary = task_service.get_daily_summary(sample_elder_id)
        
        assert summary is not None
        assert summary["total_tasks"] >= 1
        assert summary["completed_count"] >= 1
        assert "summary_text" in summary
        assert len(summary["summary_text"]) > 0
