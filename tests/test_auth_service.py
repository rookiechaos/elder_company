"""
Unit tests for AuthService
"""
import pytest
from datetime import datetime, timedelta

from services.auth_service import AuthService
from models.auth_models import UserAuthDB


class TestAuthService:
    """Test cases for AuthService"""
    
    @pytest.fixture
    def auth_service(self, db_session):
        """Create AuthService instance"""
        return AuthService(db_session, secret_key="test_secret_key_for_testing_only")
    
    def test_hash_password(self, auth_service):
        """Test password hashing"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format
    
    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False
    
    def test_create_user_success(self, auth_service, sample_user_auth_data):
        """Test creating a user successfully"""
        result = auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"],
            password=sample_user_auth_data["password"],
            username=sample_user_auth_data["username"]
        )
        
        assert result["user_id"] == sample_user_auth_data["user_id"]
        assert result["email"] == sample_user_auth_data["email"]
        assert result["is_active"] is True
        
        # Verify password is hashed
        user = auth_service.db.query(UserAuthDB).filter(
            UserAuthDB.user_id == sample_user_auth_data["user_id"]
        ).first()
        assert user.password_hash is not None
        assert user.password_hash != sample_user_auth_data["password"]
    
    def test_create_user_duplicate(self, auth_service, sample_user_auth_data):
        """Test creating duplicate user raises error"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"]
        )
        
        with pytest.raises(ValueError, match="already exists"):
            auth_service.create_user(
                user_id=sample_user_auth_data["user_id"],
                email="different@example.com"
            )
    
    def test_create_user_duplicate_email(self, auth_service, sample_user_auth_data):
        """Test creating user with duplicate email raises error"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"]
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.create_user(
                user_id="different_user_id",
                email=sample_user_auth_data["email"]
            )
    
    def test_authenticate_user_success(self, auth_service, sample_user_auth_data):
        """Test successful user authentication"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"],
            password=sample_user_auth_data["password"]
        )
        
        result = auth_service.authenticate(
            identifier=sample_user_auth_data["email"],
            password=sample_user_auth_data["password"]
        )
        
        assert result is not None
        assert result["user_id"] == sample_user_auth_data["user_id"]
    
    def test_authenticate_user_wrong_password(self, auth_service, sample_user_auth_data):
        """Test authentication with wrong password"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"],
            password=sample_user_auth_data["password"]
        )
        
        result = auth_service.authenticate(
            identifier=sample_user_auth_data["email"],
            password="wrong_password"
        )
        
        assert result is None
    
    def test_authenticate_user_not_found(self, auth_service):
        """Test authentication with non-existent user"""
        result = auth_service.authenticate(
            identifier="nonexistent@example.com",
            password="any_password"
        )
        
        assert result is None
    
    def test_create_access_token(self, auth_service, sample_user_auth_data):
        """Test creating JWT access token"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"]
        )
        
        token = auth_service.generate_token(sample_user_auth_data["user_id"])
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self, auth_service, sample_user_auth_data):
        """Test verifying valid token"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"]
        )
        
        token = auth_service.generate_token(sample_user_auth_data["user_id"])
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == sample_user_auth_data["user_id"]
    
    def test_verify_token_invalid(self, auth_service):
        """Test verifying invalid token"""
        invalid_token = "invalid_token_string"
        payload = auth_service.verify_token(invalid_token)
        
        assert payload is None
    
    def test_register_device(self, auth_service, sample_user_auth_data):
        """Test registering a device"""
        auth_service.create_user(
            user_id=sample_user_auth_data["user_id"],
            email=sample_user_auth_data["email"]
        )
        
        device_info = {
            "device_type": "mobile",
            "device_name": "Test Device",
            "os": "iOS",
            "os_version": "17.0"
        }
        
        result = auth_service.register_device(
            user_id=sample_user_auth_data["user_id"],
            device_token="test_device_token_001",
            device_info=device_info
        )
        
        assert result["user_id"] == sample_user_auth_data["user_id"]
        assert "device_token" in result