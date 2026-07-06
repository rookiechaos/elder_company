"""
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class KnowledgeBaseDB(Base):
    """Knowledge base document table"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True)
    
    # Basic information
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    doc_type = Column(String, nullable=False, index=True)  # medical, diet, care_guide
    category = Column(String, nullable=True, index=True)
    
    # Source fields
    source = Column(String, nullable=True)  # Source (e.g. MHLW)
    source_url = Column(String, nullable=True)
    
    # Tags and category
    tags = Column(JSON, nullable=True)  # List[str]
    
    # Vector embedding (for RAG)
    embedding = Column(JSON, nullable=True)  # List[float] - stored embedding vector
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=True)
    created_by = Column(String, index=True, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_public = Column(Boolean, default=False)  # Public flag
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)  # Extra metadata
    view_count = Column(Integer, default=0)  # View count
    search_count = Column(Integer, default=0)  # Search count
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FamilyMemberDB(Base):
    """Family member table"""
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    elder_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Basic information
    name = Column(String, nullable=False)
    name_ja = Column(String, nullable=True)
    name_zh = Column(String, nullable=True)
    relationship = Column(String, nullable=False, index=True)  # son, daughter, spouse, etc.
    
    # Contact info
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    
    # Notification preferences
    notification_preferences = Column(JSON, nullable=True)  # {"tasks": true, "schedules": true, "emergency": true}
    
    # Permission settings
    can_view_tasks = Column(Boolean, default=True)
    can_view_schedules = Column(Boolean, default=True)
    can_view_emotions = Column(Boolean, default=False)  # Emotions hidden by default
    can_view_activities = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)  # Verified flag
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)


class NotificationDB(Base):
    """Notification table"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String, unique=True, index=True)
    
    # Recipient fields
    recipient_type = Column(String, nullable=False, index=True)  # caregiver, elder, family_member
    recipient_id = Column(String, nullable=False, index=True)
    
    # Notification fields
    notification_type = Column(String, nullable=False, index=True)  # task_reminder, schedule_reminder, emergency, etc.
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationship / linkage fields
    related_task_id = Column(String, nullable=True, index=True)
    related_schedule_id = Column(String, nullable=True, index=True)
    related_activity_id = Column(String, nullable=True, index=True)
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Delivery fields
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    delivery_method = Column(String, nullable=True)  # push, email, sms, in_app
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
