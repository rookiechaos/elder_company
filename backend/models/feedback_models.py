"""
Feedback Models - User feedback and suggestions
Feedback models - user feedback and suggestions
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from datetime import datetime
from models.database import Base


class FeedbackDB(Base):
    """User feedback table"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)  # User ID (optional; anonymous feedback supported)
    org_id = Column(String, index=True, nullable=True)  # Organization ID
    
    # Feedback type
    feedback_type = Column(String, index=True, nullable=False)  # suggestion, bug, question, complaint, praise
    category = Column(String, index=True, nullable=True)  # feature, ui, performance, translation, other
    
    # Feedback content
    title = Column(String, nullable=False)  # Title
    content = Column(Text, nullable=False)  # Content
    attachments = Column(JSON, nullable=True)  # Attachment list（URLs）
    
    # Contact info (optional)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    
    # Status management
    status = Column(String, default="pending")  # pending, reviewing, resolved, rejected, closed
    priority = Column(String, default="normal")  # low, normal, high, urgent
    
    # Handling fields
    assigned_to = Column(String, nullable=True)  # Assigned to (admin ID)
    resolution = Column(Text, nullable=True)  # Resolution / reply
    resolved_at = Column(DateTime, nullable=True)  # Resolved at
    resolved_by = Column(String, nullable=True)  # Resolved by
    
    # Metadata
    user_agent = Column(String, nullable=True)  # User agent
    ip_address = Column(String, nullable=True)  # IP address
    page_url = Column(String, nullable=True)  # Page URL when feedback was submitted
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeedbackCommentDB(Base):
    """Feedback comment table (discussion thread)"""
    __tablename__ = "feedback_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    feedback_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # Commenter user ID
    is_admin = Column(Boolean, default=False)  # Admin comment flag
    
    # Comment body
    content = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # Attachment list
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SatisfactionSurveyDB(Base):
    """Satisfaction survey table"""
    __tablename__ = "satisfaction_surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Survey fields
    survey_type = Column(String, nullable=False)  # onboarding, feature, general, nps
    ratings = Column(JSON, nullable=False)  # Per-item ratings {"overall": 5, "ease_of_use": 4, ...}
    comments = Column(Text, nullable=True)  # Comment
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
