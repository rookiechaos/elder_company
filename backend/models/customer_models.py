"""
Customer Information Models - For personalization optimization
Customer data models for personalization
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class CustomerDB(Base):
    """Customer master table (caregiver or elder)"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)  # Customer unique ID
    customer_type = Column(String, nullable=False, index=True)  # caregiver, elder, family_member
    
    # Basic information
    name = Column(String, nullable=False)
    name_ja = Column(String, nullable=True)  # Japanese name
    name_zh = Column(String, nullable=True)  # Legacy English display name (column name retained for compatibility)
    
    # Contact info
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)
    
    # Personal info
    gender = Column(String, nullable=True)  # male, female, other
    birth_date = Column(DateTime, nullable=True)  # Birth date
    age = Column(Integer, nullable=True)  # Age (computed)
    
    # Address fields
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    prefecture = Column(String, nullable=True)  # Prefecture (Japan)
    country = Column(String, default="Japan")
    
    # Language fields
    native_language = Column(String, default="ja")  # Native language
    spoken_languages = Column(JSON, nullable=True)  # Spoken languages
    preferred_language = Column(String, default="ja")  # Preferred language
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=True)  # Organization ID
    user_id = Column(String, index=True, nullable=True)  # Linked user ID (if caregiver)
    
    # Status
    is_active = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    caregiver_profile = relationship("CaregiverProfileDB", backref="customer", uselist=False, cascade="all, delete-orphan")
    elder_profile = relationship("ElderProfileDB", backref="customer", uselist=False, cascade="all, delete-orphan")


class CaregiverProfileDB(Base):
    """Caregiver profile table"""
    __tablename__ = "caregiver_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), unique=True, index=True)
    
    # Professional info
    role = Column(String, nullable=True)  # Role: nurse, aide, family, etc.
    certification = Column(JSON, nullable=True)  # Certifications
    experience_years = Column(Integer, nullable=True)  # Years of care experience
    
    # Work info
    work_shift = Column(String, nullable=True)  # day, night, both
    work_schedule = Column(JSON, nullable=True)  # Work schedule
    specialties = Column(JSON, nullable=True)  # Specialties: ["dementia", "rehabilitation"]
    
    # Care preferences
    preferred_care_style = Column(String, nullable=True)  # gentle, active, balanced
    communication_style = Column(String, nullable=True)  # formal, casual, warm
    
    # Personalization settings
    translation_preferences = Column(JSON, nullable=True)  # Translation preferences
    activity_preferences = Column(JSON, nullable=True)  # Activity preferences
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ElderProfileDB(Base):
    """Elder profile table"""
    __tablename__ = "elder_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), unique=True, index=True)
    
    # Health status
    health_status = Column(String, nullable=True)  # good, fair, poor
    health_conditions = Column(JSON, nullable=True)  # Conditions: ["dementia", "diabetes", "hypertension"]
    mobility_level = Column(String, nullable=True)  # normal, limited, bedridden
    cognitive_level = Column(String, nullable=True)  # normal, mild_impairment, moderate, severe
    
    # Activities of daily living
    adl_scores = Column(JSON, nullable=True)  # ADL scores
    iadl_scores = Column(JSON, nullable=True)  # IADL scores
    
    # Interests and hobbies
    interests = Column(JSON, nullable=True)  # Interests: ["crafts", "music", "reading"]
    hobbies = Column(JSON, nullable=True)  # Hobbies list
    favorite_topics = Column(JSON, nullable=True)  # Favorite topics
    
    # Personal background
    occupation_history = Column(String, nullable=True)  # Occupation history
    family_info = Column(JSON, nullable=True)  # Family info
    life_story = Column(Text, nullable=True)  # Life story (key memories)
    
    # Communication preferences
    communication_preferences = Column(JSON, nullable=True)  # Communication preferences
    preferred_communication_style = Column(String, nullable=True)  # Preferred communication style
    
    # Activity capabilities
    activity_capabilities = Column(JSON, nullable=True)  # Capabilities: ["can sit", "can use hands", "can walk"]
    activity_limitations = Column(JSON, nullable=True)  # Activity limitations
    
    # Mood and personality
    personality_traits = Column(JSON, nullable=True)  # Personality traits
    mood_patterns = Column(JSON, nullable=True)  # Emotion patterns
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CareRelationshipDB(Base):
    """Care relationship table (caregiver-elder link)"""
    __tablename__ = "care_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    relationship_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    caregiver_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    elder_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    org_id = Column(String, index=True, nullable=True)
    
    # Relationship fields
    relationship_type = Column(String, nullable=True)  # professional, family, volunteer
    relationship_start_date = Column(DateTime, nullable=True)  # Relationship start date
    relationship_status = Column(String, default="active")  # active, inactive, ended
    
    # Care frequency
    care_frequency = Column(String, nullable=True)  # daily, weekly, occasional
    care_duration_hours = Column(Float, nullable=True)  # Hours per care session
    
    # Relationship quality metrics
    interaction_quality = Column(Float, nullable=True)  # Interaction quality score 0-10
    communication_effectiveness = Column(Float, nullable=True)  # Communication effectiveness score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PersonalizationDataDB(Base):
    """Personalization data table (recommendations and translation)"""
    __tablename__ = "personalization_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    data_type = Column(String, index=True)  # translation_pref, activity_pref, communication_pref
    
    # Personalization payload
    preference_data = Column(JSON, nullable=False)  # Preference data (JSON)
    
    # Data source
    source = Column(String, nullable=True)  # explicit, inferred, learned
    confidence_score = Column(Float, default=0.5)  # Confidence score 0-1
    
    # Usage statistics
    usage_count = Column(Integer, default=0)  # Usage count
    last_used_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BehaviorLogDB(Base):
    """Behavior log table (preference learning)"""
    __tablename__ = "behavior_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    caregiver_id = Column(String, index=True, nullable=True)  # Caregiver ID when subject is elder
    elder_id = Column(String, index=True, nullable=True)  # Elder ID when subject is caregiver
    org_id = Column(String, index=True, nullable=True)
    
    # Behavior type
    behavior_type = Column(String, index=True)  # translation, activity, communication, search
    action = Column(String, nullable=True)  # Specific action
    
    # Behavior payload
    behavior_data = Column(JSON, nullable=True)  # Behavior-related payload
    
    # Context fields
    context = Column(JSON, nullable=True)  # Behavior context
    
    # Outcome
    outcome = Column(String, nullable=True)  # success, failure, partial
    feedback = Column(JSON, nullable=True)  # User feedback
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Device info
    device_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)  # Session ID


class PreferenceLearningDB(Base):
    """Preference learning table"""
    __tablename__ = "preference_learning"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    customer_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    relationship_id = Column(String, index=True, nullable=True)  # Relationship-scoped preference
    
    # Learned preferences
    learned_preferences = Column(JSON, nullable=False)  # Learned preference payload
    
    # Learning source
    source_behaviors = Column(JSON, nullable=True)  # Source behavior IDs
    learning_method = Column(String, nullable=True)  # pattern_analysis, ml_model, rule_based
    
    # Confidence score
    confidence_score = Column(Float, default=0.5)  # Confidence score
    sample_size = Column(Integer, default=0)  # Sample size
    
    # Validation
    is_validated = Column(Boolean, default=False)  # Verified flag
    validation_method = Column(String, nullable=True)  # explicit, implicit, inferred
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified_at = Column(DateTime, nullable=True)


class InteractionHistoryDB(Base):
    """Interaction history table"""
    __tablename__ = "interaction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String, unique=True, index=True)
    
    # Relationship / linkage fields
    caregiver_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    elder_id = Column(String, ForeignKey("customers.customer_id"), index=True)
    relationship_id = Column(String, index=True, nullable=True)
    
    # Interaction type
    interaction_type = Column(String, index=True)  # translation, activity, conversation, care_task
    
    # Interaction content
    content = Column(Text, nullable=True)  # Interaction content
    content_metadata = Column(JSON, nullable=True)  # ContentMetadata
    
    # Interaction quality
    quality_score = Column(Float, nullable=True)  # Quality score
    engagement_level = Column(String, nullable=True)  # high, medium, low
    satisfaction_score = Column(Float, nullable=True)  # Satisfaction score
    
    # Mood and feedback
    elder_mood_before = Column(String, nullable=True)
    elder_mood_after = Column(String, nullable=True)
    caregiver_feedback = Column(Text, nullable=True)
    elder_feedback = Column(Text, nullable=True)
    
    # Timestamps
    interaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
