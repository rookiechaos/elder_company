"""
Support Models - Support ticket system
Support models - ticket system
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from datetime import datetime
from models.database import Base


class SupportTicketDB(Base):
    """Support ticket table"""
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)  # User ID
    org_id = Column(String, index=True, nullable=True)  # Organization ID
    
    # Ticket fields
    subject = Column(String, nullable=False)  # Subject
    description = Column(Text, nullable=False)  # Description
    category = Column(String, index=True, nullable=False)  # technical, billing, feature, other
    subcategory = Column(String, nullable=True)  # Subcategory
    
    # Status management
    status = Column(String, default="open", index=True)  # open, in_progress, waiting, resolved, closed
    priority = Column(String, default="normal", index=True)  # low, normal, high, urgent
    
    # Assignment fields
    assigned_to = Column(String, nullable=True)  # Assigned to (support staff ID)
    assigned_at = Column(DateTime, nullable=True)
    
    # Resolution fields
    resolution = Column(Text, nullable=True)  # Resolution text
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    
    # Metadata
    attachments = Column(JSON, nullable=True)  # Attachment list
    tags = Column(JSON, nullable=True)  # Tags
    extra_metadata = Column(JSON, nullable=True)  # Other metadata (metadata is SQLAlchemy reserved)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_response_at = Column(DateTime, nullable=True)  # First response time
    last_response_at = Column(DateTime, nullable=True)  # Last response time


class TicketMessageDB(Base):
    """Ticket message table"""
    __tablename__ = "ticket_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    ticket_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # Sender user ID
    is_internal = Column(Boolean, default=False)  # Internal message (hidden from user)
    is_admin = Column(Boolean, default=False)  # Admin message flag
    
    # Message body
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # Attachment list
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TicketActivityDB(Base):
    """Ticket activity log table"""
    __tablename__ = "ticket_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    ticket_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # Actor user ID
    
    # Activity fields
    activity_type = Column(String, nullable=False)  # created, updated, assigned, status_changed, priority_changed, etc.
    activity_data = Column(JSON, nullable=True)  # Activity payload
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
