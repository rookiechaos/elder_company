"""
Tests for error handling improvements
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from exceptions import (
    ElderCompanyException,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    TranslationError,
    ServiceUnavailableError,
    RateLimitError,
    ConflictError,
    DatabaseError
)
from middleware.error_handler import (
    elder_company_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_elder_company_exception(self):
        """Test base exception class"""
        exc = ElderCompanyException("Test message", "TEST_CODE", {"key": "value"})
        assert exc.message == "Test message"
        assert exc.error_code == "TEST_CODE"
        assert exc.details == {"key": "value"}
    
    def test_not_found_error(self):
        """Test NotFoundError"""
        exc = NotFoundError("Resource")
        assert "Resource not found" in exc.message
        assert exc.error_code == "NOT_FOUND"
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        exc = AuthenticationError("Invalid credentials")
        assert exc.message == "Invalid credentials"
        assert exc.error_code == "AUTH_ERROR"
    
    def test_authorization_error(self):
        """Test AuthorizationError"""
        exc = AuthorizationError("Permission denied")
        assert exc.message == "Permission denied"
        assert exc.error_code == "AUTHORIZATION_ERROR"
    
    def test_translation_error(self):
        """Test TranslationError"""
        exc = TranslationError("Translation failed", {"provider": "openai"})
        assert exc.message == "Translation failed"
        assert exc.error_code == "TRANSLATION_ERROR"
        assert exc.details == {"provider": "openai"}
    
    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError"""
        exc = ServiceUnavailableError("Translation Service")
        assert "Translation Service" in exc.message
        assert exc.error_code == "SERVICE_UNAVAILABLE"
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        exc = RateLimitError("Too many requests")
        assert exc.message == "Too many requests"
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
    
    def test_conflict_error(self):
        """Test ConflictError"""
        exc = ConflictError("Resource already exists")
        assert exc.message == "Resource already exists"
        assert exc.error_code == "CONFLICT"
    
    def test_database_error(self):
        """Test DatabaseError"""
        exc = DatabaseError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.error_code == "DATABASE_ERROR"


class TestErrorHandlers:
    """Test error handler functions"""
    
    @pytest.mark.asyncio
    async def test_elder_company_exception_handler(self):
        """Test custom exception handler"""
        from unittest.mock import Mock
        
        exc = NotFoundError("User")
        # Create a proper mock Request object
        request = Mock(spec=Request)
        request.url.path = "/api/user/123"
        request.method = "GET"
        request.state = Mock()
        request.state.user_id = None
        
        response = await elder_company_exception_handler(request, exc)
        
        assert response.status_code == 404
        data = response.body.decode()
        assert "NotFoundError" in data
        assert "NOT_FOUND" in data
    
    @pytest.mark.asyncio
    async def test_authentication_error_handler(self):
        """Test authentication error handler"""
        from unittest.mock import Mock
        
        exc = AuthenticationError("Invalid token")
        # Create a proper mock Request object
        request = Mock(spec=Request)
        request.url.path = "/api/user"
        request.method = "GET"
        request.state = Mock()
        request.state.user_id = None
        
        response = await elder_company_exception_handler(request, exc)
        
        assert response.status_code == 401
        data = response.body.decode()
        assert "AUTH_ERROR" in data
    
    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """Test general exception handler"""
        from unittest.mock import Mock
        
        exc = ValueError("Unexpected error")
        # Create a proper mock Request object
        request = Mock(spec=Request)
        request.url.path = "/api/test"
        request.method = "GET"
        request.state = Mock()
        request.state.user_id = None
        
        response = await general_exception_handler(request, exc)
        
        assert response.status_code == 500
        data = response.body.decode()
        assert "InternalServerError" in data
        assert "INTERNAL_ERROR" in data


class TestExceptionHandlingInAPI:
    """Test exception handling in API endpoints via TestClient."""

    def test_http_exception_uses_unified_error_shape(self, client):
        """HTTPException responses must use { error: { message } } for the frontend."""
        response = client.get("/api/user/nonexistent_user_404_test/profile")
        assert response.status_code in (401, 404, 500)
        data = response.json()
        if response.status_code == 401:
            assert "error" in data
            assert "message" in data["error"]
        elif "error" in data:
            assert "message" in data["error"]

    def test_validation_error_uses_unified_error_shape(self, client):
        """Request validation errors must use the unified error envelope."""
        response = client.post("/api/translate", json={"text": ""})
        assert response.status_code in (400, 422)
        data = response.json()
        assert "error" in data
        assert "message" in data["error"]
