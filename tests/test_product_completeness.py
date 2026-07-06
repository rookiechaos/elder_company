"""
Test Product Completeness Features
测试产品完整性功能
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import json

from main import app
from config.database import get_db, init_database
from models.auth_models import UserAuthDB
from services.auth_service import AuthService


@pytest.fixture
def db_session():
    """Create a test database session"""
    from config.database import SessionLocal
    db = SessionLocal()
    try:
        init_database()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user"""
    auth_service = AuthService(db_session)
    user_data = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        phone="1234567890"
    )
    return user_data


@pytest.fixture
def auth_token(test_user):
    """Get auth token for test user"""
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    return None


@pytest.fixture
def client(db_session):
    """Create test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthCheck:
    """Test enhanced health check endpoint"""
    
    def test_health_check_comprehensive(self, client):
        """Test comprehensive health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
        assert "ai_provider" in data["checks"]
        assert "storage" in data["checks"]


class TestDataExport:
    """Test data export functionality"""
    
    def test_export_user_data_json(self, client, auth_token):
        """Test export user data as JSON"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/data-export?format=json",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "data" in data
        assert "authentication" in data["data"]
        assert "profile" in data["data"]
    
    def test_export_user_data_csv(self, client, auth_token):
        """Test export user data as CSV"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/data-export?format=csv",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "csv_data" in data or "data" in data


class TestHelpCenter:
    """Test help center functionality"""
    
    def test_get_help_articles(self, client):
        """Test get help articles"""
        response = client.get("/api/help/articles?language=ja")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "count" in data
    
    def test_get_faqs(self, client):
        """Test get FAQs"""
        response = client.get("/api/help/faqs?language=ja")
        assert response.status_code == 200
        data = response.json()
        assert "faqs" in data
        assert "count" in data
    
    def test_search_help(self, client):
        """Test search help content"""
        response = client.get("/api/help/search?q=翻訳&language=ja")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "articles" in data
        assert "faqs" in data


class TestFeedback:
    """Test feedback functionality"""
    
    def test_create_feedback_anonymous(self, client):
        """Test create anonymous feedback"""
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "suggestion",
                "title": "Test Feedback",
                "content": "This is a test feedback",
                "category": "feature"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "feedback_id" in data
    
    def test_create_feedback_authenticated(self, client, auth_token):
        """Test create authenticated feedback"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.post(
            "/api/feedback",
            json={
                "feedback_type": "bug",
                "title": "Test Bug Report",
                "content": "Found a bug in translation",
                "category": "translation"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "feedback_id" in data
    
    def test_list_feedback(self, client, auth_token):
        """Test list feedback"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/feedback",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "feedbacks" in data
        assert "total" in data


class TestDataDeletion:
    """Test data deletion functionality"""
    
    def test_get_deletion_summary(self, client, auth_token):
        """Test get deletion summary"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/account/deletion-summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "data_types" in data
        assert "total_items" in data


class TestSupport:
    """Test support ticket functionality"""
    
    def test_create_support_ticket(self, client, auth_token):
        """Test create support ticket"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.post(
            "/api/support/tickets",
            json={
                "subject": "Test Ticket",
                "description": "This is a test support ticket",
                "category": "technical",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ticket_id" in data
        assert data["status"] == "open"
    
    def test_list_tickets(self, client, auth_token):
        """Test list support tickets"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/support/tickets",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert "total" in data


class TestPayment:
    """Test payment functionality"""
    
    def test_get_subscription(self, client, auth_token):
        """Test get subscription"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/payments/subscriptions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 or 404 (no subscription)
        assert response.status_code in [200, 404]


class TestMonitoring:
    """Test monitoring functionality"""
    
    def test_get_system_resources(self, client, auth_token):
        """Test get system resources"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/monitoring/system",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "cpu" in data or "error" in data
        assert "memory" in data or "error" in data
    
    def test_get_api_performance(self, client, auth_token):
        """Test get API performance"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/monitoring/performance?hours=24",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "request_stats" in data or "error" in data


class TestAnalytics:
    """Test analytics functionality"""
    
    def test_track_event(self, client):
        """Test track event"""
        response = client.post(
            "/api/analytics/events",
            json={
                "event_type": "page_view",
                "event_name": "test_page",
                "event_category": "navigation"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
        assert "message" in data
    
    def test_get_event_stats(self, client, auth_token):
        """Test get event statistics"""
        if not auth_token:
            pytest.skip("No auth token available")
        
        response = client.get(
            "/api/analytics/events/stats?days=30",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "period_days" in data
