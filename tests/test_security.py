"""
Security Tests - Test security features and validations
安全测试 - 测试安全功能和验证
"""

import pytest
from utils.security import (
    validate_password_strength,
    sanitize_for_logging,
    validate_jwt_secret_key,
    sanitize_input,
    validate_file_upload,
    generate_secure_token
)


class TestPasswordValidation:
    """Test password strength validation"""
    
    def test_empty_password(self):
        """Test empty password"""
        is_valid, msg = validate_password_strength("")
        assert not is_valid
        assert "empty" in msg.lower()
    
    def test_short_password(self):
        """Test password too short"""
        is_valid, msg = validate_password_strength("Short1!")
        assert not is_valid
        assert "8 characters" in msg
    
    def test_weak_password(self):
        """Test common weak password"""
        is_valid, msg = validate_password_strength("password")
        assert not is_valid
    
    def test_missing_uppercase(self):
        """Test password without uppercase"""
        is_valid, msg = validate_password_strength("lowercase123!")
        assert not is_valid
        assert "uppercase" in msg.lower()
    
    def test_missing_lowercase(self):
        """Test password without lowercase"""
        is_valid, msg = validate_password_strength("UPPERCASE123!")
        assert not is_valid
        assert "lowercase" in msg.lower()
    
    def test_missing_digit(self):
        """Test password without digit"""
        is_valid, msg = validate_password_strength("NoDigitsHere!")
        assert not is_valid
        assert "digit" in msg.lower()
    
    def test_missing_special_char(self):
        """Test password without special character"""
        is_valid, msg = validate_password_strength("NoSpecial123")
        assert not is_valid
        assert "special" in msg.lower()
    
    def test_strong_password(self):
        """Test strong password"""
        is_valid, msg = validate_password_strength("StrongP@ssw0rd!")
        assert is_valid
        assert msg is None
    
    def test_too_long_password(self):
        """Test password too long"""
        long_password = "A" * 129 + "1!"
        is_valid, msg = validate_password_strength(long_password)
        assert not is_valid
        assert "128" in msg


class TestSanitization:
    """Test input sanitization"""
    
    def test_sanitize_for_logging(self):
        """Test sensitive data sanitization in logs"""
        data = {
            "password": "secret123",
            "token": "abc123xyz",
            "api_key": "key_1234567890",
            "user_id": "user1",
            "normal_field": "value"
        }
        
        sanitized = sanitize_for_logging(data)
        
        assert sanitized["password"] == "secr***t123"
        # Token length > 8, so shows first 4 and last 4 chars
        assert sanitized["token"] == "abc1***3xyz"
        assert "***" in sanitized["api_key"]
        assert sanitized["user_id"] == "user1"  # Not sensitive
        assert sanitized["normal_field"] == "value"
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        # Test null bytes removal
        text = "Hello\x00World"
        sanitized = sanitize_input(text)
        assert "\x00" not in sanitized
        
        # Test trimming
        text = "  Hello World  "
        sanitized = sanitize_input(text)
        assert sanitized == "Hello World"
        
        # Test length limit
        text = "A" * 200
        sanitized = sanitize_input(text, max_length=100)
        assert len(sanitized) == 100
    
    def test_sanitize_empty_input(self):
        """Test empty input sanitization"""
        sanitized = sanitize_input("")
        assert sanitized == ""
        
        sanitized = sanitize_input("   ")
        assert sanitized == ""


class TestJWTSecretValidation:
    """Test JWT secret key validation"""
    
    def test_weak_secret_key(self):
        """Test weak secret key"""
        assert not validate_jwt_secret_key("secret")
        assert not validate_jwt_secret_key("password")
        assert not validate_jwt_secret_key("your-secret-key-change-in-production")
    
    def test_short_secret_key(self):
        """Test secret key too short"""
        assert not validate_jwt_secret_key("short")
        assert not validate_jwt_secret_key("a" * 31)
    
    def test_strong_secret_key(self):
        """Test strong secret key"""
        assert validate_jwt_secret_key("a" * 32)
        assert validate_jwt_secret_key("a" * 64)


class TestFileUploadValidation:
    """Test file upload validation"""
    
    def test_valid_file(self):
        """Test valid file upload"""
        is_valid, msg = validate_file_upload(
            filename="audio.wav",
            content_type="audio/wav",
            allowed_extensions=["wav", "mp3"]
        )
        assert is_valid
        assert msg is None
    
    def test_invalid_extension(self):
        """Test invalid file extension"""
        is_valid, msg = validate_file_upload(
            filename="script.exe",
            allowed_extensions=["wav", "mp3"]
        )
        assert not is_valid
        assert "not allowed" in msg.lower()
    
    def test_path_traversal(self):
        """Test path traversal attempt"""
        is_valid, msg = validate_file_upload(
            filename="../../../etc/passwd",
            allowed_extensions=["wav"]
        )
        assert not is_valid
        assert "invalid" in msg.lower()
    
    def test_empty_filename(self):
        """Test empty filename"""
        is_valid, msg = validate_file_upload(filename="")
        assert not is_valid
        assert "required" in msg.lower()


class TestTokenGeneration:
    """Test secure token generation"""
    
    def test_generate_token(self):
        """Test token generation"""
        token1 = generate_secure_token()
        token2 = generate_secure_token()
        
        assert len(token1) == 64  # 32 bytes = 64 hex chars
        assert len(token2) == 64
        assert token1 != token2  # Should be unique
    
    def test_custom_length(self):
        """Test custom token length"""
        token = generate_secure_token(length=16)
        assert len(token) == 32  # 16 bytes = 32 hex chars
