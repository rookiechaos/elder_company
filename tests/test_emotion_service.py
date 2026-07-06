"""
Emotion Service Unit Tests
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from services.emotion_service import EmotionService, get_emotion_service
from models.task_models import EmotionLogDB
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
def emotion_service(db_session):
    """Create emotion service instance"""
    return get_emotion_service(db_session)


@pytest.fixture
def sample_user_id():
    """Sample user ID"""
    return "user_test_123"


class TestEmotionService:
    """Emotion service test class"""
    
    def test_log_emotion(self, emotion_service, sample_user_id):
        """Test log emotion"""
        emotion_log = emotion_service.log_emotion(
            user_id=sample_user_id,
            user_type="elder",
            emotion_score=4,
            emotion_type="happy",
            notes="Feeling good today"
        )
        
        assert emotion_log is not None
        assert emotion_log["user_id"] == sample_user_id
        assert emotion_log["user_type"] == "elder"
        assert emotion_log["emotion_score"] == 4
        assert emotion_log["emotion_type"] == "happy"
        assert "log_id" in emotion_log
    
    def test_log_emotion_invalid_score(self, emotion_service, sample_user_id):
        """Test invalid emotion score"""
        with pytest.raises(ValueError):
            emotion_service.log_emotion(
                user_id=sample_user_id,
                user_type="elder",
                emotion_score=6  # Invalid score
            )
        
        with pytest.raises(ValueError):
            emotion_service.log_emotion(
                user_id=sample_user_id,
                user_type="elder",
                emotion_score=0  # Invalid score
            )
    
    def test_log_emotion_invalid_type(self, emotion_service, sample_user_id):
        """Test invalid user type"""
        with pytest.raises(ValueError):
            emotion_service.log_emotion(
                user_id=sample_user_id,
                user_type="invalid_type",
                emotion_score=3
            )
    
    def test_get_emotion_history(self, emotion_service, sample_user_id):
        """Test get emotion history"""
        # Log multiple emotions
        emotion_service.log_emotion(
            user_id=sample_user_id,
            user_type="elder",
            emotion_score=4,
            emotion_type="happy"
        )
        emotion_service.log_emotion(
            user_id=sample_user_id,
            user_type="elder",
            emotion_score=3,
            emotion_type="calm"
        )
        
        # Get emotion history
        history = emotion_service.get_emotion_history(sample_user_id)
        
        assert len(history) >= 2
        assert all(log["user_id"] == sample_user_id for log in history)
    
    def test_get_emotion_analysis(self, emotion_service, sample_user_id):
        """Test get emotion analysis"""
        # Log multiple emotions
        for i in range(5):
            emotion_service.log_emotion(
                user_id=sample_user_id,
                user_type="elder",
                emotion_score=4,
                emotion_type="happy"
            )
        
        # Get analysis
        analysis = emotion_service.get_emotion_analysis(sample_user_id, days=30)
        
        assert analysis is not None
        assert analysis["user_id"] == sample_user_id
        assert analysis["total_logs"] >= 5
        assert "average_score" in analysis
        assert "trend" in analysis
        assert "emotion_distribution" in analysis
        assert "patterns" in analysis
    
    def test_generate_positive_feedback(self, emotion_service):
        """Test generate positive feedback"""
        context = {
            "completed_tasks": ["Take medication", "Walk"],
            "emotion_score": 4,
            "recent_activities": ["origami"]
        }
        
        feedback = emotion_service.generate_positive_feedback(
            elder_id="elder_123",
            caregiver_id="caregiver_123",
            context=context
        )
        
        assert feedback is not None
        assert len(feedback) > 0
        assert isinstance(feedback, str)
    
    def test_detect_stress(self, emotion_service):
        """Test stress detection"""
        # Create low emotion logs
        emotion_logs = [
            {"emotion_score": 2},
            {"emotion_score": 1},
            {"emotion_score": 2}
        ]
        
        stress_result = emotion_service.detect_stress(
            caregiver_id="caregiver_123",
            emotion_logs=emotion_logs
        )
        
        assert stress_result is not None
        assert "stress_level" in stress_result
        assert "stress_score" in stress_result
        assert "signals" in stress_result
        assert "suggestions" in stress_result
        assert stress_result["stress_level"] in ["low", "medium", "high"]
        assert 1 <= stress_result["stress_score"] <= 10
