"""
Database Models - Data models only, no configuration
Database models only (no configuration)
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Base class for all models
Base = declarative_base()


class OrganizationDB(Base):
    """Organization (care facility) table"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String, unique=True, index=True)  # Organization unique ID
    name = Column(String, nullable=False)  # Organization name
    name_ja = Column(String, nullable=True)  # Organization name (Japanese)
    
    # Organization fields
    org_type = Column(String, nullable=True)  # Org type: nursing home, health facility, etc.
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    # Organization configuration
    default_source_language = Column(String, default="ja")
    default_target_language = Column(String, default="zh")
    org_custom_terms = Column(JSON, nullable=True)  # Org-level custom terms
    org_care_scenarios = Column(JSON, nullable=True)  # Org care scenario presets
    
    # Subscription and limits
    subscription_plan = Column(String, default="basic")  # basic, professional, enterprise
    max_users = Column(Integer, default=10)  # Max users
    monthly_translation_limit = Column(Integer, default=1000)  # Monthly translation quota
    
    # Statistics
    total_translations = Column(Integer, default=0)  # Total translations
    active_users_count = Column(Integer, default=0)  # Active user count
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserProfileDB(Base):
    """User profile settings table"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    org_id = Column(String, index=True, nullable=True)  # Organization ID
    
    # Personal info
    name = Column(String, nullable=True)
    name_ja = Column(String, nullable=True)  # Japanese name
    role = Column(String, nullable=True)  # Caregiver role: nurse, family, etc.
    experience_years = Column(Integer, nullable=True)  # Years of care experience
    
    # Language preferences
    preferred_source_language = Column(String, default="ja")
    preferred_target_language = Column(String, default="zh")
    
    # Translation preferences
    translation_style = Column(String, default="professional")  # professional, casual, formal
    detail_level = Column(String, default="moderate")  # brief, moderate, detailed
    use_honorifics = Column(Boolean, default=True)  # Use honorifics
    
    # Care scenario preferences
    care_scenarios = Column(JSON, nullable=True)  # Frequent care scenarios
    custom_terms = Column(JSON, nullable=True)  # Custom term dictionary
    
    # Work habits
    work_shift = Column(String, nullable=True)  # Work shift: day, night, both
    common_tasks = Column(JSON, nullable=True)  # Common task list
    
    # Personalization settings
    preferences = Column(JSON, nullable=True)  # Other preferences
    
    # Permissions and status
    user_role = Column(String, default="caregiver")  # caregiver, admin, manager
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TranslationHistoryDB(Base):
    """Translation history table"""
    __tablename__ = "translation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    org_id = Column(String, index=True, nullable=True)  # Organization ID
    
    original_text = Column(Text)
    translated_text = Column(Text)
    source_language = Column(String)
    target_language = Column(String)
    context = Column(String, nullable=True)
    
    # Statistics fields
    text_length = Column(Integer, nullable=True)  # Source text length
    translation_time_ms = Column(Integer, nullable=True)  # Translation duration (ms)
    provider = Column(String, nullable=True)  # AI provider used
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class UsageStatisticsDB(Base):
    """Usage statistics table (org/user/date)"""
    __tablename__ = "usage_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String, index=True, nullable=True)
    user_id = Column(String, index=True, nullable=True)
    
    date = Column(String, index=True)  # YYYY-MM-DD format
    translation_count = Column(Integer, default=0)
    total_characters = Column(Integer, default=0)
    
    # Language-pair statistics
    language_pairs = Column(JSON, nullable=True)  # {"ja-zh": 100, "zh-ja": 50}
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityTemplateDB(Base):
    """Activity template library"""
    __tablename__ = "activity_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(String, unique=True, index=True)
    
    # Basic information
    title_ja = Column(String, nullable=False)
    title_zh = Column(String, nullable=False)
    title_en = Column(String, nullable=True)
    description_ja = Column(Text, nullable=True)
    description_zh = Column(Text, nullable=True)
    
    # Category and tags
    category = Column(String, index=True)  # cognitive, craft, music, exercise, social, etc.
    tags = Column(JSON, nullable=True)  # ["memory training", "crafts", "relaxing"]
    
    # Applicability
    difficulty_level = Column(String, default="medium")  # easy, medium, hard
    duration_minutes = Column(Integer, nullable=True)
    required_materials = Column(JSON, nullable=True)  # Required materials list
    participant_count = Column(String, default="1-2")  # Participant count
    
    # Suitable audience
    suitable_for = Column(JSON, nullable=True)  # ["dementia", "limited mobility", "bedridden"]
    health_considerations = Column(JSON, nullable=True)  # Health considerations
    
    # Activity content
    steps = Column(JSON, nullable=True)  # Activity steps
    tips = Column(Text, nullable=True)  # Activity tips
    variations = Column(JSON, nullable=True)  # Activity variants
    
    # Metadata
    created_by = Column(String, nullable=True)  # Creator (org or system)
    usage_count = Column(Integer, default=0)  # Usage count
    rating = Column(Float, default=0.0)  # Average rating
    
    # Sharing and community
    is_shared = Column(Boolean, default=False)  # Shared to community
    share_count = Column(Integer, default=0)  # Share count
    view_count = Column(Integer, default=0)  # View count
    
    # Multimedia
    images = Column(JSON, nullable=True)  # Image URL list
    videos = Column(JSON, nullable=True)  # Video URL list
    audio = Column(JSON, nullable=True)  # Audio URL list
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityRecordDB(Base):
    """Activity record table"""
    __tablename__ = "activity_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=True)
    caregiver_id = Column(String, index=True)  # Caregiver ID
    elder_id = Column(String, index=True, nullable=True)  # Elder ID (optional)
    
    # Activity fields
    activity_template_id = Column(String, index=True, nullable=True)  # Source template ID
    activity_title = Column(String, nullable=False)
    activity_category = Column(String, nullable=True)
    
    # Activity details
    customized_steps = Column(JSON, nullable=True)  # Customized activity steps
    materials_used = Column(JSON, nullable=True)  # Materials actually used
    
    # Activity session
    duration_minutes = Column(Integer, nullable=True)  # Actual duration (minutes)
    notes = Column(Text, nullable=True)  # Activity notes
    
    # Effectiveness evaluation
    elder_engagement = Column(String, nullable=True)  # high, medium, low
    elder_mood_before = Column(String, nullable=True)  # Mood before activity
    elder_mood_after = Column(String, nullable=True)  # Mood after activity
    caregiver_feedback = Column(Text, nullable=True)  # Caregiver feedback
    elder_feedback = Column(Text, nullable=True)  # Elder feedback (if any)
    
    # Outcomes record
    photos = Column(JSON, nullable=True)  # Activity photo URLs
    videos = Column(JSON, nullable=True)  # Activity video URLs
    achievements = Column(JSON, nullable=True)  # Activity outcome description
    
    # Co-design
    co_designed_by = Column(JSON, nullable=True)  # Co-designer list [{"user_id": "...", "role": "caregiver/elder/family"}]
    design_notes = Column(Text, nullable=True)  # Design notes
    
    # Family participation
    family_members = Column(JSON, nullable=True)  # Participating family members
    family_feedback = Column(JSON, nullable=True)  # Family feedback
    
    # Voice-related fields
    voice_notes = Column(JSON, nullable=True)  # Voice note URLs
    transcription = Column(Text, nullable=True)  # Speech-to-text
    
    # Metadata
    activity_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityRecommendationDB(Base):
    """Activity recommendation record table"""
    __tablename__ = "activity_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=True)
    caregiver_id = Column(String, index=True)
    elder_id = Column(String, index=True, nullable=True)
    
    # Recommendation fields
    recommended_activities = Column(JSON, nullable=False)  # Recommended activities
    recommendation_reason = Column(Text, nullable=True)  # Recommendation rationale
    elder_profile = Column(JSON, nullable=True)  # Elder profile snapshot
    
    # Recommendation status
    status = Column(String, default="pending")  # pending, accepted, rejected, completed
    selected_activity_id = Column(String, nullable=True)  # Selected activity ID
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database initialization moved to config/database.py
# This file contains only data models
