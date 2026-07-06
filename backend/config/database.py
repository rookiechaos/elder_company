"""
Database Configuration - Separated from business logic

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from config.settings import settings

load_dotenv()

# Database URL from settings
DATABASE_URL = settings.get_database_url()

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=settings.database_pool_pre_ping  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session (dependency for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables"""
    from models.database import Base
    
    # Import all models to ensure they're registered
    try:
        from models.auth_models import (
            UserAuthDB, DeviceDB, SyncLogDB, DataVersionDB, ApiKeyDB
        )
    except ImportError:
        pass
    
    try:
        from models.customer_models import (
            CustomerDB, CaregiverProfileDB, ElderProfileDB,
            CareRelationshipDB, PersonalizationDataDB,
            BehaviorLogDB, PreferenceLearningDB, InteractionHistoryDB
        )
    except ImportError:
        pass
    
    try:
        from models.help_models import HelpArticleDB, FAQDB, HelpFeedbackDB
    except ImportError:
        pass
    
    try:
        from models.feedback_models import FeedbackDB, FeedbackCommentDB, SatisfactionSurveyDB
    except ImportError:
        pass
    
    try:
        from models.support_models import SupportTicketDB, TicketMessageDB, TicketActivityDB
    except ImportError:
        pass
    
    try:
        from models.payment_models import PaymentDB, SubscriptionDB, InvoiceDB
    except ImportError:
        pass
    
    try:
        from models.analytics_models import UserEventDB, UserSessionDB, FunnelStepDB
    except ImportError:
        pass
    
    try:
        from models.task_models import TaskDB, ScheduleDB, EmotionLogDB
    except ImportError:
        pass
    
    try:
        from models.knowledge_models import KnowledgeBaseDB, FamilyMemberDB, NotificationDB
    except ImportError:
        pass
    
    try:
        from models.summary_models import InfoChangeLogDB, CustomerSummaryDB, ConversationHistoryDB
    except ImportError:
        pass
    
    try:
        from models.emergency_models import EmergencyRecordDB, NightModeConfigDB
    except ImportError:
        pass
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_engine():
    """Get database engine (for migrations, etc.)"""
    return engine


def setup_query_analysis():
    """Setup query analysis for the database engine"""
    try:
        from services.query_analyzer import setup_query_analysis as setup_analyzer
        slow_query_threshold = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))
        return setup_analyzer(engine, slow_query_threshold)
    except ImportError:
        # Query analyzer not available
        return None
