"""
Unit tests for API routes
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app
from config.database import get_db


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestTranslationEndpoint:
    """Test translation endpoints"""
    
    @pytest.mark.asyncio
    @patch('services.translation_service.TranslationService.translate')
    async def test_translate_success(self, mock_translate, client):
        """Test successful translation"""
        mock_translate.return_value = {
            "translated_text": "你好",
            "original_text": "こんにちは",
            "source_language": "ja",
            "target_language": "zh"
        }
        
        response = client.post(
            "/api/translate",
            json={
                "text": "こんにちは",
                "source_language": "ja",
                "target_language": "zh"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "你好"
        assert data["original_text"] == "こんにちは"
    
    def test_translate_empty_text(self, client):
        """Test translation with empty text"""
        response = client.post(
            "/api/translate",
            json={
                "text": "",
                "source_language": "ja",
                "target_language": "zh"
            }
        )
        
        assert response.status_code == 400
    
    def test_translate_invalid_language(self, client):
        """Test translation with invalid language"""
        response = client.post(
            "/api/translate",
            json={
                "text": "Hello",
                "source_language": "invalid",
                "target_language": "zh"
            }
        )
        
        # Should either accept or return 400/422
        assert response.status_code in [200, 400, 422]


class TestCustomerEndpoint:
    """Test customer endpoints"""
    
    def test_create_customer_success(self, client):
        """Test creating a customer"""
        response = client.post(
            "/api/customers",
            json={
                "customer_id": "test_customer_001",
                "customer_type": "caregiver",
                "name": "测试看护者",
                "name_ja": "テスト介護者",
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "test_customer_001"
        assert data["customer_type"] == "caregiver"
    
    def test_get_customer_by_id(self, client):
        """Test getting customer by ID"""
        # First create a customer
        create_response = client.post(
            "/api/customers",
            json={
                "customer_id": "test_customer_002",
                "customer_type": "caregiver",
                "name": "测试看护者2"
            }
        )
        assert create_response.status_code == 200
        
        # Then get it
        response = client.get("/api/customers/test_customer_002")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "test_customer_002"
    
    def test_get_customer_not_found(self, client):
        """Test getting non-existent customer"""
        response = client.get("/api/customers/non_existent")
        assert response.status_code == 404
