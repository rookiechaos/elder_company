"""
Integration Tests
Test collaboration across multiple services
"""

import pytest
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session

from services.task_service import get_task_service
from services.schedule_service import get_schedule_service
from services.emotion_service import get_emotion_service
from services.family_service import get_family_service
from services.notification_service import get_notification_service
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


class TestTaskScheduleIntegration:
    """Task and schedule integration tests"""
    
    def test_task_and_schedule_integration(self, db_session):
        """Test task and schedule integration"""
        caregiver_id = "caregiver_integration_123"
        elder_id = "elder_integration_456"
        
        task_service = get_task_service(db_session)
        schedule_service = get_schedule_service(db_session)
        
        # Create task
        task = task_service.create_task(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            title="Take medication",
            task_type="medication",
            due_date=utc_now() + timedelta(hours=1)
        )
        
        # Create linked schedule
        schedule = schedule_service.create_schedule(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            title="Take medication时间",
            schedule_type="medication",
            start_time=utc_now() + timedelta(hours=1),
            related_task_id=task["task_id"]
        )
        
        assert schedule["related_task_id"] == task["task_id"]
        
        # Complete task
        completed_task = task_service.complete_task(
            task_id=task["task_id"],
            completed_by=caregiver_id
        )
        
        assert completed_task["status"] == "completed"


class TestEmotionTaskIntegration:
    """Emotion and task integration tests"""
    
    def test_emotion_with_task(self, db_session):
        """Test emotion logging linked to tasks"""
        user_id = "user_integration_123"
        task_id = "task_integration_456"
        
        emotion_service = get_emotion_service(db_session)
        
        # Log task-related emotion
        emotion_log = emotion_service.log_emotion(
            user_id=user_id,
            user_type="elder",
            emotion_score=4,
            emotion_type="happy",
            related_task_id=task_id
        )
        
        assert emotion_log["related_task_id"] == task_id


class TestFamilyNotificationIntegration:
    """Family member and notification integration tests"""
    
    def test_family_notification_flow(self, db_session):
        """Test family member notification flow"""
        elder_id = "elder_integration_123"
        caregiver_id = "caregiver_integration_456"
        
        family_service = get_family_service(db_session)
        notification_service = get_notification_service(db_session)
        
        # Add family member
        family_member = family_service.add_family_member(
            elder_id=elder_id,
            name="田中太郎",
            relationship="son",
            email="tanaka@example.com",
            notification_preferences={
                "tasks": True,
                "schedules": True,
                "emergency": True
            }
        )
        
        # Send family member notification
        notifications = notification_service.send_family_notification(
            elder_id=elder_id,
            notification_type="task_reminder",
            title="タスクリマインダー",
            content="お薬を飲む時間です"
        )
        
        assert len(notifications) >= 1
        assert any(n["recipient_id"] == family_member["member_id"] for n in notifications)


class TestDailyWorkflowIntegration:
    """Daily workflow integration tests"""
    
    def test_daily_workflow(self, db_session):
        """Test complete daily workflow"""
        caregiver_id = "caregiver_workflow_123"
        elder_id = "elder_workflow_456"
        
        task_service = get_task_service(db_session)
        schedule_service = get_schedule_service(db_session)
        emotion_service = get_emotion_service(db_session)
        
        # 1. Create task
        task = task_service.create_task(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            title="Walk",
            task_type="exercise"
        )
        
        # 2. 创建日程
        schedule = schedule_service.create_schedule(
            caregiver_id=caregiver_id,
            elder_id=elder_id,
            title="Walk时间",
            schedule_type="exercise",
            start_time=utc_now() + timedelta(hours=1)
        )
        
        # 3. Complete task
        completed_task = task_service.complete_task(
            task_id=task["task_id"],
            completed_by=caregiver_id
        )
        
        # 4. Log emotion
        emotion_log = emotion_service.log_emotion(
            user_id=elder_id,
            user_type="elder",
            emotion_score=4,
            emotion_type="happy",
            related_task_id=task["task_id"]
        )
        
        # 5. Get daily summary
        summary = task_service.get_daily_summary(elder_id)
        
        assert completed_task["status"] == "completed"
        assert emotion_log["emotion_score"] == 4
        assert summary["completed_count"] >= 1
