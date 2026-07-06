"""
Tests for Custom Exceptions
自定义异常测试
"""

import pytest

from exceptions import (
    ElderCompanyException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    CustomerNotFoundError,
    UserNotFoundError,
    TranslationError,
    ServiceUnavailableError,
    RateLimitError,
    ConflictError,
    DatabaseError
)


def test_elder_company_exception_base():
    """Test base exception"""
    exc = ElderCompanyException("Test message", "TEST_CODE", {"key": "value"})
    
    assert str(exc) == "Test message"
    assert exc.message == "Test message"
    assert exc.error_code == "TEST_CODE"
    assert exc.details == {"key": "value"}


def test_authentication_error():
    """Test authentication error"""
    exc = AuthenticationError("Invalid credentials")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "AUTH_ERROR"
    assert exc.message == "Invalid credentials"


def test_authorization_error():
    """Test authorization error"""
    exc = AuthorizationError("Permission denied", {"user_id": "123"})
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "AUTHORIZATION_ERROR"
    assert exc.details == {"user_id": "123"}


def test_validation_error():
    """Test validation error"""
    exc = ValidationError("Invalid input")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "VALIDATION_ERROR"


def test_not_found_error():
    """Test not found error"""
    exc = NotFoundError("Resource")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "NOT_FOUND"
    assert "Resource" in exc.message


def test_customer_not_found_error():
    """Test customer not found error"""
    exc = CustomerNotFoundError(customer_id="customer_123")
    
    assert isinstance(exc, NotFoundError)
    assert exc.details == {"customer_id": "customer_123"}


def test_user_not_found_error():
    """Test user not found error"""
    exc = UserNotFoundError(user_id="user_123")
    
    assert isinstance(exc, NotFoundError)
    assert exc.details == {"user_id": "user_123"}


def test_translation_error():
    """Test translation error"""
    exc = TranslationError("Translation failed")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "TRANSLATION_ERROR"


def test_service_unavailable_error():
    """Test service unavailable error"""
    exc = ServiceUnavailableError("AI Service")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "SERVICE_UNAVAILABLE"
    assert exc.details == {"service": "AI Service"}


def test_rate_limit_error():
    """Test rate limit error"""
    exc = RateLimitError("Too many requests")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "RATE_LIMIT_EXCEEDED"


def test_conflict_error():
    """Test conflict error"""
    exc = ConflictError("Resource already exists")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "CONFLICT"


def test_database_error():
    """Test database error"""
    exc = DatabaseError("Connection failed")
    
    assert isinstance(exc, ElderCompanyException)
    assert exc.error_code == "DATABASE_ERROR"
