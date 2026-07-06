"""
API Key Service - API key authentication and management
"""

import secrets
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.auth_models import ApiKeyDB


class ApiKeyService:
    """Service for API key management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_api_key(self) -> str:
        """Generate a new API key"""
        # Generate a secure random key
        key = f"ek_{secrets.token_urlsafe(32)}"  # ek = Elder Company
        return key
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    def create_api_key(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        key_name: Optional[str] = None,
        key_type: str = "user",
        permissions: Optional[Dict[str, Any]] = None,
        rate_limit: str = "100/minute",
        max_requests_per_day: Optional[int] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new API key
        
        Args:
            user_id: Associated user ID (optional)
            org_id: Associated organization ID (optional)
            key_name: Key name/description
            key_type: Key type (user, org, system)
            permissions: Permissions dictionary
            rate_limit: Rate limit string (e.g., "100/minute")
            max_requests_per_day: Maximum requests per day
            expires_in_days: Key expiration in days (None = no expiration)
        
        Returns:
            Dict with api_key (only shown once) and key info
        """
        # Generate API key
        api_key = self.generate_api_key()
        api_key_hash = self.hash_api_key(api_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = utc_now() + timedelta(days=expires_in_days)
        
        # Create API key record
        key_db = ApiKeyDB(
            api_key_hash=api_key_hash,
            user_id=user_id,
            org_id=org_id,
            key_name=key_name or f"API Key {utc_now().strftime('%Y-%m-%d')}",
            key_type=key_type,
            permissions=permissions or {},
            rate_limit=rate_limit,
            max_requests_per_day=max_requests_per_day,
            expires_at=expires_at,
            is_active=True
        )
        
        self.db.add(key_db)
        self.db.commit()
        self.db.refresh(key_db)
        
        # Return key info (api_key only shown once)
        return {
            "api_key": api_key,  # Only shown once!
            "key_id": key_db.id,
            "key_name": key_db.key_name,
            "key_type": key_db.key_type,
            "created_at": key_db.created_at.isoformat(),
            "expires_at": key_db.expires_at.isoformat() if key_db.expires_at else None,
            "rate_limit": key_db.rate_limit,
            "max_requests_per_day": key_db.max_requests_per_day,
            "warning": "Please save this API key. It will not be shown again."
        }
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Verify API key and return key info
        
        Args:
            api_key: API key to verify
        
        Returns:
            Key info dict if valid, None otherwise
        """
        api_key_hash = self.hash_api_key(api_key)
        
        # Find key
        key_db = self.db.query(ApiKeyDB).filter(
            and_(
                ApiKeyDB.api_key_hash == api_key_hash,
                ApiKeyDB.is_active == True
            )
        ).first()
        
        if not key_db:
            return None
        
        # Check expiration
        if key_db.expires_at and key_db.expires_at < utc_now():
            return None
        
        # Update usage stats
        key_db.total_requests += 1
        key_db.last_used_at = utc_now()
        self.db.commit()
        
        return {
            "key_id": key_db.id,
            "user_id": key_db.user_id,
            "org_id": key_db.org_id,
            "key_name": key_db.key_name,
            "key_type": key_db.key_type,
            "permissions": key_db.permissions or {},
            "rate_limit": key_db.rate_limit,
            "max_requests_per_day": key_db.max_requests_per_day,
            "total_requests": key_db.total_requests
        }
    
    def get_api_keys(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all API keys for user or org"""
        query = self.db.query(ApiKeyDB).filter(ApiKeyDB.is_active == True)
        
        if user_id:
            query = query.filter(ApiKeyDB.user_id == user_id)
        if org_id:
            query = query.filter(ApiKeyDB.org_id == org_id)
        
        keys = query.all()
        
        return [
            {
                "key_id": key.id,
                "key_name": key.key_name,
                "key_type": key.key_type,
                "user_id": key.user_id,
                "org_id": key.org_id,
                "rate_limit": key.rate_limit,
                "max_requests_per_day": key.max_requests_per_day,
                "total_requests": key.total_requests,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "created_at": key.created_at.isoformat(),
                "is_active": key.is_active
            }
            for key in keys
        ]
    
    def revoke_api_key(self, key_id: int) -> bool:
        """Revoke (deactivate) an API key"""
        key_db = self.db.query(ApiKeyDB).filter(
            ApiKeyDB.id == key_id
        ).first()
        
        if not key_db:
            return False
        
        key_db.is_active = False
        key_db.updated_at = utc_now()
        self.db.commit()
        
        return True
    
    def update_api_key(
        self,
        key_id: int,
        key_name: Optional[str] = None,
        rate_limit: Optional[str] = None,
        max_requests_per_day: Optional[int] = None,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update API key settings"""
        key_db = self.db.query(ApiKeyDB).filter(
            ApiKeyDB.id == key_id
        ).first()
        
        if not key_db:
            raise ValueError(f"API key {key_id} not found")
        
        if key_name:
            key_db.key_name = key_name
        if rate_limit:
            key_db.rate_limit = rate_limit
        if max_requests_per_day is not None:
            key_db.max_requests_per_day = max_requests_per_day
        if expires_in_days is not None:
            if expires_in_days == 0:
                key_db.expires_at = None
            else:
                key_db.expires_at = utc_now() + timedelta(days=expires_in_days)
        
        key_db.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(key_db)
        
        return {
            "key_id": key_db.id,
            "key_name": key_db.key_name,
            "rate_limit": key_db.rate_limit,
            "max_requests_per_day": key_db.max_requests_per_day,
            "expires_at": key_db.expires_at.isoformat() if key_db.expires_at else None
        }


# Global API key service instance
_api_key_service: Optional[ApiKeyService] = None


def get_api_key_service(db: Session) -> ApiKeyService:
    """Get API key service instance"""
    return ApiKeyService(db)
