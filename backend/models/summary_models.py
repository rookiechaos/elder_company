"""
Summary and Change Tracking Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class InfoChangeLogDB(Base):
    """Information change log table"""
    __tablename__ = "info_change_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    change_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Change fields
    change_type = Column(String, nullable=False, index=True)  # created, updated, deleted
    field_name = Column(String, nullable=False)  # Changed field name
    old_value = Column(Text, nullable=True)  # Old value
    new_value = Column(Text, nullable=True)  # New value
    
    # Change details
    change_summary = Column(Text, nullable=True)  # Change summary
    change_category = Column(String, nullable=True, index=True)  # health, personal, preferences, etc.
    
    # Relationship / linkage fields
    changed_by = Column(String, nullable=True)  # Changed-by user ID
    related_task_id = Column(String, nullable=True, index=True)
    related_schedule_id = Column(String, nullable=True, index=True)
    
    # Timestamps
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerSummaryDB(Base):
    """Customer summary cache table"""
    __tablename__ = "customer_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Summary data
    summary_type = Column(String, nullable=False, index=True)  # full, health, preferences, activities
    summary_text = Column(Text, nullable=False)  # Summary text
    summary_data = Column(JSON, nullable=True)  # Structured summary data
    
    # Key info fields
    key_info = Column(JSON, nullable=True)  # Key info (needs, mood, health, etc.)
    last_updated_fields = Column(JSON, nullable=True)  # Recently updated field names
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Summary expiry time
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationHistoryDB(Base):
    """RAG conversation history table (multi-turn)"""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)  # User ID (optional)
    elder_id = Column(String, index=True, nullable=True)  # Elder ID (optional)
    org_id = Column(String, index=True, nullable=True)
    
    # Conversation fields
    messages = Column(JSON, nullable=False)  # Conversation messages
    context_docs = Column(JSON, nullable=True)  # Referenced document IDs
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    last_message_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
