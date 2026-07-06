"""
Permission Service - Role-based access control
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from enum import Enum

from models.database import UserProfileDB
from exceptions import AuthorizationError, UserNotFoundError


class Role(str, Enum):
    """User roles"""
    CAREGIVER = "caregiver"
    ADMIN = "admin"
    MANAGER = "manager"
    SUPPORT = "support"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permissions"""
    # User management
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # Organization management
    VIEW_ORGANIZATION = "view_organization"
    EDIT_ORGANIZATION = "edit_organization"
    MANAGE_ORGANIZATION = "manage_organization"
    
    # Support tickets
    VIEW_TICKETS = "view_tickets"
    CREATE_TICKETS = "create_tickets"
    EDIT_TICKETS = "edit_tickets"
    ASSIGN_TICKETS = "assign_tickets"
    CLOSE_TICKETS = "close_tickets"
    
    # Monitoring
    VIEW_MONITORING = "view_monitoring"
    VIEW_ANALYTICS = "view_analytics"
    
    # Feedback
    VIEW_FEEDBACK = "view_feedback"
    MANAGE_FEEDBACK = "manage_feedback"
    
    # Payment
    VIEW_PAYMENTS = "view_payments"
    MANAGE_PAYMENTS = "manage_payments"
    
    # Data export/deletion
    EXPORT_DATA = "export_data"
    DELETE_DATA = "delete_data"


# Role-Permission mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.CAREGIVER: [
        Permission.VIEW_USERS,
        Permission.CREATE_TICKETS,
        Permission.VIEW_TICKETS,
        Permission.EXPORT_DATA,
    ],
    Role.MANAGER: [
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,
        Permission.VIEW_ORGANIZATION,
        Permission.EDIT_ORGANIZATION,
        Permission.VIEW_TICKETS,
        Permission.EDIT_TICKETS,
        Permission.ASSIGN_TICKETS,
        Permission.VIEW_MONITORING,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FEEDBACK,
        Permission.EXPORT_DATA,
    ],
    Role.ADMIN: [
        Permission.VIEW_USERS,
        Permission.CREATE_USERS,
        Permission.EDIT_USERS,
        Permission.DELETE_USERS,
        Permission.VIEW_ORGANIZATION,
        Permission.EDIT_ORGANIZATION,
        Permission.MANAGE_ORGANIZATION,
        Permission.VIEW_TICKETS,
        Permission.CREATE_TICKETS,
        Permission.EDIT_TICKETS,
        Permission.ASSIGN_TICKETS,
        Permission.CLOSE_TICKETS,
        Permission.VIEW_MONITORING,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_FEEDBACK,
        Permission.MANAGE_FEEDBACK,
        Permission.VIEW_PAYMENTS,
        Permission.MANAGE_PAYMENTS,
        Permission.EXPORT_DATA,
        Permission.DELETE_DATA,
    ],
    Role.SUPPORT: [
        Permission.VIEW_TICKETS,
        Permission.EDIT_TICKETS,
        Permission.ASSIGN_TICKETS,
        Permission.CLOSE_TICKETS,
        Permission.VIEW_FEEDBACK,
        Permission.VIEW_USERS,
    ],
    Role.VIEWER: [
        Permission.VIEW_USERS,
        Permission.VIEW_ORGANIZATION,
        Permission.VIEW_TICKETS,
        Permission.VIEW_MONITORING,
    ],
}


from services.base_service import BaseService


class PermissionService(BaseService):
    """Service for checking user permissions"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def get_user_role(self, user_id: str) -> Role:
        """Get user role"""
        profile = self.db.query(UserProfileDB).filter(
            UserProfileDB.user_id == user_id
        ).first()
        
        if not profile:
            raise UserNotFoundError(user_id=user_id)
        
        # Get role from profile, default to CAREGIVER
        role_str = getattr(profile, "user_role", "caregiver")
        try:
            return Role(role_str.lower())
        except ValueError:
            return Role.CAREGIVER
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        try:
            role = self.get_user_role(user_id)
            user_permissions = ROLE_PERMISSIONS.get(role, [])
            return permission in user_permissions
        except UserNotFoundError:
            return False
    
    def require_permission(self, user_id: str, permission: Permission) -> None:
        """Require a permission, raise AuthorizationError if not granted"""
        if not self.has_permission(user_id, permission):
            role = self.get_user_role(user_id)
            raise AuthorizationError(
                f"Permission denied: {permission.value} required, but user has role {role.value}",
                details={
                    "user_id": user_id,
                    "required_permission": permission.value,
                    "user_role": role.value
                }
            )
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        try:
            role = self.get_user_role(user_id)
            return role == Role.ADMIN
        except UserNotFoundError:
            return False
    
    def is_manager_or_admin(self, user_id: str) -> bool:
        """Check if user is manager or admin"""
        try:
            role = self.get_user_role(user_id)
            return role in [Role.MANAGER, Role.ADMIN]
        except UserNotFoundError:
            return False
    
    def is_support_staff(self, user_id: str) -> bool:
        """Check if user is support staff"""
        try:
            role = self.get_user_role(user_id)
            return role in [Role.SUPPORT, Role.ADMIN]
        except UserNotFoundError:
            return False
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        try:
            role = self.get_user_role(user_id)
            return ROLE_PERMISSIONS.get(role, [])
        except UserNotFoundError:
            return []


def get_permission_service(db: Session) -> PermissionService:
    """Get permission service instance"""
    return PermissionService(db)
