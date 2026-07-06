"""
Custom Exceptions - Application-specific exception classes

"""

from typing import Optional, Dict, Any


class ElderCompanyException(Exception):
    """Base exception for Elder Company application"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(ElderCompanyException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTH_ERROR", details)


class AuthorizationError(ElderCompanyException):
    """Authorization related errors (permission denied)"""
    
    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ValidationError(ElderCompanyException):
    """Validation error"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(ElderCompanyException):
    """Resource not found error"""
    
    def __init__(self, resource: str = "Resource", details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        super().__init__(message, "NOT_FOUND", details)


class CustomerNotFoundError(NotFoundError):
    """Customer not found"""
    
    def __init__(self, customer_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"Customer not found" + (f": {customer_id}" if customer_id else "")
        super().__init__("Customer", details or {"customer_id": customer_id})


class UserNotFoundError(NotFoundError):
    """User not found"""
    
    def __init__(self, user_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"User not found" + (f": {user_id}" if user_id else "")
        super().__init__("User", details or {"user_id": user_id})


class OrganizationNotFoundError(NotFoundError):
    """Organization not found"""
    
    def __init__(self, org_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"Organization not found" + (f": {org_id}" if org_id else "")
        super().__init__("Organization", details or {"org_id": org_id})


class TranslationError(ElderCompanyException):
    """Translation service error"""
    
    def __init__(self, message: str = "Translation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "TRANSLATION_ERROR", details)


class ServiceUnavailableError(ElderCompanyException):
    """Service unavailable error"""
    
    def __init__(self, service: str = "Service", details: Optional[Dict[str, Any]] = None):
        message = f"{service} is currently unavailable"
        super().__init__(message, "SERVICE_UNAVAILABLE", details or {"service": service})


class RateLimitError(ElderCompanyException):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class ConflictError(ElderCompanyException):
    """Resource conflict error (e.g., duplicate entry)"""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT", details)


class DatabaseError(ElderCompanyException):
    """Database operation error"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)
