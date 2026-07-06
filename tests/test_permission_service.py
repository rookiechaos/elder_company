"""
Tests for Permission Service
权限服务测试
"""

import pytest
from sqlalchemy.orm import Session

from services.permission_service import PermissionService, Permission, Role, get_permission_service
from models.database import UserProfileDB
from exceptions import UserNotFoundError, AuthorizationError


def test_get_user_role_caregiver(db_session: Session):
    """Test getting caregiver role"""
    # Create a user profile with caregiver role
    profile = UserProfileDB(
        user_id="test_user_1",
        user_role="caregiver"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    role = service.get_user_role("test_user_1")
    
    assert role == Role.CAREGIVER


def test_get_user_role_admin(db_session: Session):
    """Test getting admin role"""
    profile = UserProfileDB(
        user_id="test_admin_1",
        user_role="admin"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    role = service.get_user_role("test_admin_1")
    
    assert role == Role.ADMIN


def test_get_user_role_not_found(db_session: Session):
    """Test getting role for non-existent user"""
    service = PermissionService(db_session)
    
    with pytest.raises(UserNotFoundError):
        service.get_user_role("non_existent_user")


def test_has_permission_caregiver(db_session: Session):
    """Test permission check for caregiver"""
    profile = UserProfileDB(
        user_id="test_caregiver",
        user_role="caregiver"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    # Caregiver should have VIEW_USERS
    assert service.has_permission("test_caregiver", Permission.VIEW_USERS) is True
    
    # Caregiver should NOT have DELETE_USERS
    assert service.has_permission("test_caregiver", Permission.DELETE_USERS) is False


def test_has_permission_admin(db_session: Session):
    """Test permission check for admin"""
    profile = UserProfileDB(
        user_id="test_admin",
        user_role="admin"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    # Admin should have all permissions
    assert service.has_permission("test_admin", Permission.DELETE_USERS) is True
    assert service.has_permission("test_admin", Permission.MANAGE_ORGANIZATION) is True
    assert service.has_permission("test_admin", Permission.VIEW_MONITORING) is True


def test_require_permission_success(db_session: Session):
    """Test requiring permission when user has it"""
    profile = UserProfileDB(
        user_id="test_manager",
        user_role="manager"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    # Should not raise exception
    service.require_permission("test_manager", Permission.VIEW_MONITORING)


def test_require_permission_failure(db_session: Session):
    """Test requiring permission when user doesn't have it"""
    profile = UserProfileDB(
        user_id="test_caregiver",
        user_role="caregiver"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    # Should raise AuthorizationError
    with pytest.raises(AuthorizationError):
        service.require_permission("test_caregiver", Permission.DELETE_USERS)


def test_is_admin(db_session: Session):
    """Test admin check"""
    admin_profile = UserProfileDB(
        user_id="test_admin",
        user_role="admin"
    )
    caregiver_profile = UserProfileDB(
        user_id="test_caregiver",
        user_role="caregiver"
    )
    db_session.add(admin_profile)
    db_session.add(caregiver_profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    assert service.is_admin("test_admin") is True
    assert service.is_admin("test_caregiver") is False


def test_is_manager_or_admin(db_session: Session):
    """Test manager or admin check"""
    admin_profile = UserProfileDB(user_id="test_admin", user_role="admin")
    manager_profile = UserProfileDB(user_id="test_manager", user_role="manager")
    caregiver_profile = UserProfileDB(user_id="test_caregiver", user_role="caregiver")
    
    db_session.add(admin_profile)
    db_session.add(manager_profile)
    db_session.add(caregiver_profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    
    assert service.is_manager_or_admin("test_admin") is True
    assert service.is_manager_or_admin("test_manager") is True
    assert service.is_manager_or_admin("test_caregiver") is False


def test_get_user_permissions(db_session: Session):
    """Test getting all permissions for a user"""
    profile = UserProfileDB(
        user_id="test_admin",
        user_role="admin"
    )
    db_session.add(profile)
    db_session.commit()
    
    service = PermissionService(db_session)
    permissions = service.get_user_permissions("test_admin")
    
    # Admin should have many permissions
    assert len(permissions) > 10
    assert Permission.DELETE_USERS in permissions
    assert Permission.MANAGE_ORGANIZATION in permissions
