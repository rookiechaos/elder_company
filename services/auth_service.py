"""
Authentication Service - User authentication and authorization
"""

import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import jwt
import bcrypt

from models.auth_models import UserAuthDB, DeviceDB
from models.database import UserProfileDB


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry = timedelta(days=30)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_method: str = "password"
    ) -> Dict[str, Any]:
        """
        Create a new user account.

        Args:
            user_id: Unique user identifier
            email: Email address (optional)
            phone: Phone number (optional)
            username: Display username (optional)
            password: Password (optional, depends on auth_method)
            auth_method: Authentication method (default: "password")

        Returns:
            Dictionary containing user auth metadata

        Raises:
            ValueError: If user_id already exists or validation fails
        """
        
        # Check if user already exists
        existing = self.db.query(UserAuthDB).filter(
            UserAuthDB.user_id == user_id
        ).first()
        
        if existing:
            raise ValueError(f"User {user_id} already exists")
        
        # Check email uniqueness
        if email:
            existing_email = self.db.query(UserAuthDB).filter(
                UserAuthDB.email == email
            ).first()
            if existing_email:
                raise ValueError("Email already registered")
        
        # Validate and hash password if provided
        password_hash = None
        if password:
            # Validate password strength
            from utils.security import validate_password_strength
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                from exceptions import ValidationError
                raise ValidationError(f"Password validation failed: {error_msg}")
            password_hash = self.hash_password(password)
        
        # Create auth record
        auth = UserAuthDB(
            user_id=user_id,
            email=email,
            phone=phone,
            username=username,
            password_hash=password_hash,
            auth_method=auth_method,
            is_active=True
        )
        
        self.db.add(auth)
        self.db.commit()
        self.db.refresh(auth)
        
        return self._auth_to_dict(auth)
    
    def authenticate(
        self,
        identifier: str,  # email, phone, or username
        password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        
        # Find user by email, phone, or username
        auth = self.db.query(UserAuthDB).filter(
            and_(
                UserAuthDB.is_active == True,
                or_(
                    UserAuthDB.email == identifier,
                    UserAuthDB.phone == identifier,
                    UserAuthDB.username == identifier
                )
            )
        ).first()
        
        if not auth:
            return None
        
        # Verify password
        if not auth.password_hash or not self.verify_password(password, auth.password_hash):
            return None
        
        # Update last login
        auth.last_login = utc_now()
        self.db.commit()
        
        return self._auth_to_dict(auth)
    
    def generate_token(self, user_id: str, device_id: Optional[str] = None) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "device_id": device_id,
            "exp": utc_now() + self.token_expiry,
            "iat": utc_now()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_device(
        self,
        user_id: str,
        device_token: str,
        device_info: Dict[str, Any],
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new device"""
        
        # Check if device already exists
        existing = self.db.query(DeviceDB).filter(
            DeviceDB.device_token == device_token
        ).first()
        
        if existing:
            # Update device info
            for key, value in device_info.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.last_seen_at = utc_now()
            existing.is_active = True
        else:
            # Create new device
            device_id = f"device_{secrets.token_hex(12)}"
            
            # Check if this is user's first device (make it primary)
            existing_devices = self.db.query(DeviceDB).filter(
                DeviceDB.user_id == user_id
            ).count()
            is_primary = existing_devices == 0
            
            device = DeviceDB(
                device_id=device_id,
                user_id=user_id,
                org_id=org_id,
                device_token=device_token,
                device_name=device_info.get("device_name"),
                device_type=device_info.get("device_type"),
                platform=device_info.get("platform"),
                device_model=device_info.get("device_model"),
                os_version=device_info.get("os_version"),
                app_version=device_info.get("app_version"),
                push_token=device_info.get("push_token"),
                is_primary=is_primary,
                is_active=True
            )
            
            self.db.add(device)
            existing = device
        
        self.db.commit()
        self.db.refresh(existing)
        
        return self._device_to_dict(existing)
    
    def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all devices for a user"""
        devices = self.db.query(DeviceDB).filter(
            and_(
                DeviceDB.user_id == user_id,
                DeviceDB.is_active == True
            )
        ).all()
        
        return [self._device_to_dict(device) for device in devices]
    
    def _auth_to_dict(self, auth: UserAuthDB) -> Dict[str, Any]:
        """Convert auth to dictionary"""
        return {
            "user_id": auth.user_id,
            "email": auth.email,
            "phone": auth.phone,
            "username": auth.username,
            "auth_method": auth.auth_method,
            "is_email_verified": auth.is_email_verified,
            "is_phone_verified": auth.is_phone_verified,
            "is_active": auth.is_active,
            "last_login": auth.last_login.isoformat() if auth.last_login else None,
            "created_at": auth.created_at.isoformat() if auth.created_at else None
        }
    
    def _device_to_dict(self, device: DeviceDB) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "device_id": device.device_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "platform": device.platform,
            "device_model": device.device_model,
            "app_version": device.app_version,
            "is_primary": device.is_primary,
            "last_sync_at": device.last_sync_at.isoformat() if device.last_sync_at else None,
            "last_seen_at": device.last_seen_at.isoformat() if device.last_seen_at else None,
            "registered_at": device.registered_at.isoformat() if device.registered_at else None
        }
