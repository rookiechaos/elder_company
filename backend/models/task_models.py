"""
Task Management Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class TaskDB(Base):
    """Task table"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    
    # Basic information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String, nullable=False, index=True)  # medication, exercise, appointment, custom
    
    # Relationship / linkage fields
    caregiver_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    elder_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    relationship_id = Column(String, index=True, nullable=True)
    
    # Participants (family members, etc.)
    family_member_ids = Column(JSON, nullable=True)  # List[str]
    
    # Task status
    status = Column(String, nullable=False, default="pending", index=True)  # pending, in_progress, completed, cancelled
    priority = Column(String, nullable=False, default="medium")  # low, medium, high
    
    # Timestamps
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Progress fields
    progress = Column(Integer, default=0)  # 0-100
    progress_notes = Column(Text, nullable=True)
    
    # Reminder settings
    reminders = Column(JSON, nullable=True)  # List[dict] - [{"time": "...", "type": "notification", "sent": false}]
    
    # Other fields
    notes = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # Extra metadata
    
    # Completion fields
    completed_by = Column(String, nullable=True)  # Completed-by user ID
    completion_notes = Column(Text, nullable=True)
    completion_summary = Column(Text, nullable=True)  # AI-generated completion summary


class ScheduleDB(Base):
    """Schedule table"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String, unique=True, index=True)
    
    # Basic information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    schedule_type = Column(String, nullable=False, index=True)  # medication, exercise, appointment, activity
    
    # Relationship / linkage fields
    caregiver_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    elder_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    org_id = Column(String, index=True, nullable=True)
    relationship_id = Column(String, index=True, nullable=True)
    
    # Timestamps
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    recurrence = Column(String, nullable=False, default="none")  # daily, weekly, monthly, custom, none
    recurrence_end_date = Column(DateTime, nullable=True)
    recurrence_pattern = Column(JSON, nullable=True)  # Custom recurrence pattern
    
    # Participants
    participants = Column(JSON, nullable=True)  # List[str] - participant user IDs
    
    # Sharing settings
    is_shared = Column(Boolean, default=True)  # Shared with family members
    shared_with = Column(JSON, nullable=True)  # List[str] - family member IDs shared with
    
    # Reminder settings
    reminders = Column(JSON, nullable=True)  # List[dict] - [{"time": "...", "type": "notification", "sent": false}]
    
    # Other fields
    notes = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    extra_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Linked task when schedule maps to a task
    related_task_id = Column(String, nullable=True, index=True)


class EmotionLogDB(Base):
    """Emotion log table"""
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True)
    
    # User fields
    user_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    user_type = Column(String, nullable=False, index=True)  # elder, caregiver
    org_id = Column(String, index=True, nullable=True)
    
    # Emotion fields
    emotion_score = Column(Integer, nullable=False)  # Score 1-5
    emotion_type = Column(String, nullable=True, index=True)  # happy, sad, anxious, calm, tired, energetic, etc.
    
    # Detailed record
    notes = Column(Text, nullable=True)  # Optional text notes
    voice_note_url = Column(String, nullable=True)  # Optional voice note URL
    
    # Context fields
    context = Column(JSON, nullable=True)  # Context (activity, weather, health, etc.)
    
    # Relationship / linkage fields
    related_task_id = Column(String, nullable=True, index=True)
    related_schedule_id = Column(String, nullable=True, index=True)
    related_activity_id = Column(String, nullable=True, index=True)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)
