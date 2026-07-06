"""
Help Center Models - Help articles and FAQ
Help center models - articles and FAQs
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from datetime import datetime
from models.database import Base


class HelpArticleDB(Base):
    """Help article table"""
    __tablename__ = "help_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(String, unique=True, index=True, nullable=False)
    
    # Article fields
    title = Column(String, nullable=False)  # Title
    title_ja = Column(String, nullable=True)  # Japanese title
    title_zh = Column(String, nullable=True)  # Chinese title
    
    content = Column(Text, nullable=False)  # Content
    content_ja = Column(Text, nullable=True)  # Japanese content
    content_zh = Column(Text, nullable=True)  # Chinese content
    
    # Category and tags
    category = Column(String, index=True, nullable=False)  # Category
    tags = Column(JSON, nullable=True)  # Tag list
    
    # Metadata
    view_count = Column(Integer, default=0)  # View count
    helpful_count = Column(Integer, default=0)  # Helpful vote count
    not_helpful_count = Column(Integer, default=0)  # Not helpful vote count
    
    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # Featured flag
    
    # Sort order
    display_order = Column(Integer, default=0)  # Display order
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FAQDB(Base):
    """FAQ table"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    faq_id = Column(String, unique=True, index=True, nullable=False)
    
    # Question fields
    question = Column(String, nullable=False)  # Question
    question_ja = Column(String, nullable=True)  # Japanese question
    question_zh = Column(String, nullable=True)  # Chinese question
    
    answer = Column(Text, nullable=False)  # Answer
    answer_ja = Column(Text, nullable=True)  # Japanese answer
    answer_zh = Column(Text, nullable=True)  # Chinese answer
    
    # Category
    category = Column(String, index=True, nullable=False)  # Category
    
    # Metadata
    view_count = Column(Integer, default=0)  # View count
    helpful_count = Column(Integer, default=0)  # Helpful vote count
    
    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # Featured flag
    
    # Sort order
    display_order = Column(Integer, default=0)  # Display order
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HelpFeedbackDB(Base):
    """Help feedback table"""
    __tablename__ = "help_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    article_id = Column(String, index=True, nullable=True)  # Linked article ID
    faq_id = Column(String, index=True, nullable=True)  # Linked FAQ ID
    user_id = Column(String, index=True, nullable=True)  # User ID (optional)
    
    # Feedback content
    feedback_type = Column(String, nullable=False)  # helpful, not_helpful, comment
    comment = Column(Text, nullable=True)  # Comment
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
