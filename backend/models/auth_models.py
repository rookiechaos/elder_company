"""
Authentication and User Management Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class UserAuthDB(Base):
    """User authentication table"""
    __tablename__ = "user_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Authentication fields
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    
    # Password (hashed)
    password_hash = Column(String, nullable=True)  # bcrypt hash
    
    # Auth method
    auth_method = Column(String, default="password")  # password, oauth_google, oauth_apple, phone
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # google, apple, wechat
    oauth_id = Column(String, nullable=True)
    
    # Device info
    devices = Column(JSON, nullable=True)  # Registered device list
    
    # Security settings
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeviceDB(Base):
    """Device info table"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Device info
    device_name = Column(String, nullable=True)  # User-defined device name
    device_type = Column(String, nullable=True)  # mobile, tablet, web
    platform = Column(String, nullable=True)  # ios, android, web
    device_model = Column(String, nullable=True)
    os_version = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    
    # Device identifiers
    device_token = Column(String, unique=True, index=True)  # Unique device ID
    push_token = Column(String, nullable=True)  # Push notification token
    
    # Sync fields
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String, default="active")  # active, inactive, error
    
    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary device flag
    
    # Metadata
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SyncLogDB(Base):
    """Data sync log table"""
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_id = Column(String, unique=True, index=True)
    
    # Sync fields
    user_id = Column(String, index=True)
    device_id = Column(String, index=True)
    sync_type = Column(String, nullable=False)  # full, incremental, conflict_resolution
    
    # Synced payload
    data_type = Column(String, nullable=False)  # profile, activities, translations, settings
    records_synced = Column(Integer, default=0)
    records_conflicted = Column(Integer, default=0)
    
    # Sync result
    status = Column(String, default="pending")  # pending, success, failed, partial
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    sync_started_at = Column(DateTime, default=datetime.utcnow)
    sync_completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class DataVersionDB(Base):
    """Data version table (conflict detection)"""
    __tablename__ = "data_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Data identifiers
    user_id = Column(String, index=True)
    data_type = Column(String, index=True)  # profile, activity_record, translation_history
    data_id = Column(String, index=True)  # Record ID
    
    # Version fields
    version = Column(Integer, default=1)  # Version number
    last_modified_by = Column(String, nullable=True)  # Last modified by device ID
    last_modified_at = Column(DateTime, default=datetime.utcnow)
    
    # Conflict flags
    has_conflict = Column(Boolean, default=False)
    conflict_resolution = Column(String, nullable=True)  # server_wins, client_wins, merged
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiKeyDB(Base):
    """API key table"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True, nullable=False)  # API key (hashed)
    api_key_hash = Column(String, nullable=False)  # Key hash
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)  # Linked user (optional)
    org_id = Column(String, index=True, nullable=True)  # Linked organization (optional)
    
    # Key metadata
    key_name = Column(String, nullable=True)  # Key name / description
    key_type = Column(String, default="user")  # user, org, system
    permissions = Column(JSON, nullable=True)  # Permission list
    
    # Usage limits
    rate_limit = Column(String, default="100/minute")  # Rate limit
    max_requests_per_day = Column(Integer, nullable=True)  # Max requests per day
    
    # Usage statistics
    total_requests = Column(Integer, default=0)  # Total request count
    last_used_at = Column(DateTime, nullable=True)  # Last used at
    last_used_ip = Column(String, nullable=True)  # Last used IP
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)  # Expiry time (optional)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
