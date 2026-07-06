"""
Schedule Service Unit Tests
"""

import pytest
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session

from services.schedule_service import ScheduleService, get_schedule_service
from models.task_models import ScheduleDB
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
def schedule_service(db_session):
    """Create schedule service instance"""
    return get_schedule_service(db_session)


@pytest.fixture
def sample_caregiver_id():
    """Sample caregiver ID"""
    return "caregiver_test_123"


@pytest.fixture
def sample_elder_id():
    """Sample elder ID"""
    return "elder_test_456"


class TestScheduleService:
    """Schedule service test class"""
    
    def test_create_schedule(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test create schedule"""
        start_time = utc_now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=30)
        
        schedule = schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test schedule",
            schedule_type="exercise",
            start_time=start_time,
            end_time=end_time
        )
        
        assert schedule is not None
        assert schedule["title"] == "Test schedule"
        assert schedule["schedule_type"] == "exercise"
        assert schedule["recurrence"] == "none"
        assert sample_caregiver_id in schedule["participants"]
        assert sample_elder_id in schedule["participants"]
        assert "schedule_id" in schedule
    
    def test_get_schedule(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test get schedule"""
        start_time = utc_now() + timedelta(hours=1)
        
        # Create schedule
        created_schedule = schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test schedule",
            schedule_type="exercise",
            start_time=start_time
        )
        
        # Get schedule
        schedule = schedule_service.get_schedule(created_schedule["schedule_id"])
        
        assert schedule is not None
        assert schedule["schedule_id"] == created_schedule["schedule_id"]
        assert schedule["title"] == "Test schedule"
    
    def test_get_schedules(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test get schedule list"""
        start_time = utc_now() + timedelta(hours=1)
        
        # Create multiple schedules
        schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Schedule 1",
            schedule_type="medication",
            start_time=start_time
        )
        schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Schedule 2",
            schedule_type="exercise",
            start_time=start_time + timedelta(hours=2)
        )
        
        # Get schedule list
        schedules = schedule_service.get_schedules(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id
        )
        
        assert len(schedules) >= 2
        assert any(s["title"] == "Schedule 1" for s in schedules)
        assert any(s["title"] == "Schedule 2" for s in schedules)
    
    def test_get_calendar_view(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test get calendar view"""
        today = utc_now()
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        
        # Create schedule
        schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test schedule",
            schedule_type="exercise",
            start_time=start_date + timedelta(hours=10)
        )
        
        # Get calendar view
        calendar = schedule_service.get_calendar_view(
            elder_id=sample_elder_id,
            start_date=start_date,
            end_date=end_date
        )
        
        assert calendar is not None
        assert "schedules_by_date" in calendar
        assert "total_schedules" in calendar
        assert calendar["total_schedules"] >= 1
    
    def test_update_schedule(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test update schedule"""
        start_time = utc_now() + timedelta(hours=1)
        
        # Create schedule
        created_schedule = schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test schedule",
            schedule_type="exercise",
            start_time=start_time
        )
        
        # Update schedule
        new_start_time = start_time + timedelta(hours=1)
        updated_schedule = schedule_service.update_schedule(
            schedule_id=created_schedule["schedule_id"],
            title="Updated schedule",
            start_time=new_start_time
        )
        
        assert updated_schedule["title"] == "Updated schedule"
        assert updated_schedule["start_time"] == new_start_time.isoformat()
    
    def test_delete_schedule(self, schedule_service, sample_caregiver_id, sample_elder_id):
        """Test delete schedule"""
        start_time = utc_now() + timedelta(hours=1)
        
        # Create schedule
        created_schedule = schedule_service.create_schedule(
            caregiver_id=sample_caregiver_id,
            elder_id=sample_elder_id,
            title="Test schedule",
            schedule_type="exercise",
            start_time=start_time
        )
        
        # Delete schedule
        success = schedule_service.delete_schedule(created_schedule["schedule_id"])
        
        assert success is True
        
        # Verify deletion
        schedule = schedule_service.get_schedule(created_schedule["schedule_id"])
        assert schedule is None
