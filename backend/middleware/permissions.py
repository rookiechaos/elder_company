"""
Permission Middleware - Role-based access control dependencies

"""

from fastapi import Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session

from api.auth_routes import get_current_user
from config.database import get_db
from services.permission_service import PermissionService, Permission, get_permission_service
from exceptions import AuthorizationError


def require_permission(permission: Permission):
    """
    Dependency to require a specific permission
    
    Usage:
        @router.get("/admin/users")
        async def get_users(
            current_user: dict = Depends(require_permission(Permission.VIEW_USERS)),
            db: Session = Depends(get_db)
        ):
            ...
    """
    async def permission_checker(
        current_user: Optional[dict] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        if not current_user:
            raise AuthorizationError("Authentication required")
        
        user_id = current_user.get("user_id")
        if not user_id:
            raise AuthorizationError("User ID not found in token")
        
        permission_service = get_permission_service(db)
        permission_service.require_permission(user_id, permission)
        
        return current_user
    
    return permission_checker


def require_admin():
    """
    Dependency to require admin role
    
    Usage:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(
            current_user: dict = Depends(require_admin()),
            db: Session = Depends(get_db)
        ):
            ...
    """
    async def admin_checker(
        current_user: Optional[dict] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        if not current_user:
            raise AuthorizationError("Authentication required")
        
        user_id = current_user.get("user_id")
        if not user_id:
            raise AuthorizationError("User ID not found in token")
        
        permission_service = get_permission_service(db)
        if not permission_service.is_admin(user_id):
            raise AuthorizationError("Admin access required")
        
        return current_user
    
    return admin_checker


def require_manager_or_admin():
    """
    Dependency to require manager or admin role
    """
    async def manager_checker(
        current_user: Optional[dict] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        if not current_user:
            raise AuthorizationError("Authentication required")
        
        user_id = current_user.get("user_id")
        if not user_id:
            raise AuthorizationError("User ID not found in token")
        
        permission_service = get_permission_service(db)
        if not permission_service.is_manager_or_admin(user_id):
            raise AuthorizationError("Manager or admin access required")
        
        return current_user
    
    return manager_checker


def require_support_staff():
    """
    Dependency to require support staff role
    """
    async def support_checker(
        current_user: Optional[dict] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        if not current_user:
            raise AuthorizationError("Authentication required")
        
        user_id = current_user.get("user_id")
        if not user_id:
            raise AuthorizationError("User ID not found in token")
        
        permission_service = get_permission_service(db)
        if not permission_service.is_support_staff(user_id):
            raise AuthorizationError("Support staff access required")
        
        return current_user
    
    return support_checker
