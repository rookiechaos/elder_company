"""
Emergency and Night Mode Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class EmergencyRecordDB(Base):
    """Emergency record table"""
    __tablename__ = "emergency_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    elder_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    caregiver_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Emergency fields
    emergency_type = Column(String, nullable=False, index=True)  # health, emotional, behavioral
    severity = Column(String, nullable=False, index=True)  # low, medium, high
    description = Column(Text, nullable=False)
    actions_taken = Column(JSON, nullable=True)  # List[str] - Actions taken
    
    # AI guidance fields
    ai_guidance = Column(Text, nullable=True)  # AI-generated guidance text
    voice_guidance_url = Column(String, nullable=True)  # Voice guidance URL (TTS)
    relief_actions = Column(JSON, nullable=True)  # List[str] - Suggested relief actions
    risk_notes = Column(Text, nullable=True)  # Risk notes
    
    # Brief report
    summary = Column(Text, nullable=True)  # Brief report (AI-generated)
    
    # Notification fields
    notified_contacts = Column(JSON, nullable=True)  # List[str] - Notified contact IDs
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)


class NightModeConfigDB(Base):
    """Night mode configuration table"""
    __tablename__ = "night_mode_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(String, unique=True, index=True)
    
    # User fields
    user_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_type = Column(String, nullable=False, index=True)  # elder, caregiver
    org_id = Column(String, index=True, nullable=True)
    
    # Night mode settings
    enabled = Column(Boolean, default=False, index=True)
    brightness = Column(String, default="low")  # low, medium, high
    sound_enabled = Column(Boolean, default=False)
    text_prompts = Column(Boolean, default=True)
    
    # Time settings
    start_time = Column(String, nullable=True)  # HH:MM format, e.g. "22:00"
    end_time = Column(String, nullable=True)  # HH:MM format, e.g. "07:00"
    
    # Sound settings
    sound_type = Column(String, nullable=True)  # gentle, calm, silent
    volume = Column(Integer, default=50)  # 0-100
    
    # UI settings
    font_size = Column(String, default="large")  # small, medium, large, extra_large
    color_scheme = Column(String, default="dark")  # dark, dim, custom
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
