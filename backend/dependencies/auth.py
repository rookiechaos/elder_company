"""
Authentication dependencies - require_auth, get_optional_user, get_auth_service_dependency
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from config.database import get_db
from config.settings import settings
from middleware.auth import get_current_user as _get_current_user
from services.auth_service import AuthService


def get_optional_user(
    current_user: Optional[Dict[str, Any]] = Depends(_get_current_user)
) -> Optional[Dict[str, Any]]:
    """Get current user, but allow None for anonymous access."""
    return current_user


def require_auth(
    current_user: Optional[Dict[str, Any]] = Depends(_get_current_user)
) -> Dict[str, Any]:
    """Require authentication. Raise HTTPException if not authenticated."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


CurrentUser = Depends(require_auth)
OptionalCurrentUser = Depends(get_optional_user)


def get_auth_service_dependency(db: Session = Depends(get_db)) -> AuthService:
    """Get auth service instance"""
    return AuthService(db, settings.jwt_secret_key)
