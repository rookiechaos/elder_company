"""
Analytics Models - User behavior tracking
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float
from datetime import datetime
from models.database import Base


class UserEventDB(Base):
    """User event table"""
    __tablename__ = "user_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)
    org_id = Column(String, index=True, nullable=True)
    session_id = Column(String, index=True, nullable=True)  # Session ID
    
    # Event fields
    event_type = Column(String, index=True, nullable=False)  # page_view, click, action, conversion, etc.
    event_name = Column(String, index=True, nullable=False)  # Event name
    event_category = Column(String, index=True, nullable=True)  # Event category
    
    # Event payload
    event_data = Column(JSON, nullable=True)  # Event payload
    properties = Column(JSON, nullable=True)  # Event properties
    
    # Context fields
    page_url = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserSessionDB(Base):
    """User session table"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Session fields
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Session payload
    page_views = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    referrer = Column(String, nullable=True)
    entry_page = Column(String, nullable=True)
    exit_page = Column(String, nullable=True)
    
    # Device info
    device_type = Column(String, nullable=True)  # mobile, tablet, desktop
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FunnelStepDB(Base):
    """Conversion funnel step table"""
    __tablename__ = "funnel_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(String, unique=True, index=True, nullable=False)
    
    # Funnel fields
    funnel_name = Column(String, index=True, nullable=False)  # Funnel name
    step_name = Column(String, nullable=False)  # Step name
    step_order = Column(Integer, nullable=False)  # Step order
    
    # Statistics fields
    user_count = Column(Integer, default=0)  # Users reaching this step
    conversion_rate = Column(Float, default=0.0)  # Conversion rate
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
