"""
Authentication Middleware
Centralized authentication utilities
"""

from typing import Optional, Dict, Any
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from services.auth_service import AuthService
from config.database import get_db
from config.settings import settings

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)  # Allow optional authentication

# Secret key for JWT (must be in environment variable)
SECRET_KEY = settings.jwt_secret_key

# Additional validation for default/weak keys
default_keys = {
    "your-secret-key-change-in-production",
    "change-me-in-production",
    "secret",
    "password",
    "123456"
}

if SECRET_KEY in default_keys:
    if settings.is_production():
        raise ValueError(
            "JWT_SECRET_KEY must be set to a secure value in production environment. "
            "Using default key is INSECURE and will cause the application to fail. "
            "Generate a secure key using: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    else:
        import warnings
        warnings.warn(
            f"JWT_SECRET_KEY is set to default value '{SECRET_KEY}'. "
            "This is INSECURE for production. "
            "Please set a strong secret key (minimum 32 characters). "
            "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'",
            UserWarning
        )

# Validate secret key strength
from utils.security import validate_jwt_secret_key
if not validate_jwt_secret_key(SECRET_KEY):
    if settings.is_production():
        raise ValueError(
            "JWT_SECRET_KEY is not secure for production. "
            "Please set a strong secret key (minimum 32 characters). "
            "Generate one using: python -c 'import secrets; print(secrets.token_hex(32))'"
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from token
    Returns None if no credentials provided (for optional auth endpoints)
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session
        
    Returns:
        User payload dict if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    auth_service = AuthService(db, SECRET_KEY)
    
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        return None  # Return None instead of raising exception for optional auth
    
    return payload
