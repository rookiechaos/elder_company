"""
Service dependencies - get_*_service_dependency for all services
"""

from sqlalchemy.orm import Session
from fastapi import Depends

from config.database import get_db
from services.customer_service import CustomerService
from services.organization_service import OrganizationService
from services.translation_service import TranslationService
from services.permission_service import PermissionService, get_permission_service
from services.support_service import SupportService
from services.feedback_service import FeedbackService
from services.analytics_service import AnalyticsService
from services.monitoring_service import MonitoringService
from services.data_export_service import DataExportService
from services.data_deletion_service import DataDeletionService
from services.help_service import HelpService
from services.payment_service import PaymentService
from services.api_key_service import ApiKeyService
from services.health_check_service import get_health_check_service
from services.emergency_service import EmergencyService
from services.night_mode_service import NightModeService
from services.emotion_service import EmotionService
from services.rag_service import RAGService
from services.summary_service import SummaryService
from services.notification_service import NotificationService
from services.task_service import TaskService
from services.schedule_service import ScheduleService
from services.activity_service import ActivityService
from services.sync_service import SyncService
from services.user_service import UserService
from services.storage_service import StorageService
from services.voice_service import VoiceService
from services.family_service import FamilyService
from services.family_participation_service import FamilyParticipationService
from services.family_feedback_service import FamilyFeedbackService


def get_customer_service_dependency(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


def get_organization_service_dependency(db: Session = Depends(get_db)) -> OrganizationService:
    return OrganizationService(db)


def get_translation_service_dependency() -> TranslationService:
    return TranslationService()


def get_permission_service_dependency(db: Session = Depends(get_db)) -> PermissionService:
    return get_permission_service(db)


def get_emergency_service_dependency(db: Session = Depends(get_db)) -> EmergencyService:
    return EmergencyService(db)


def get_night_mode_service_dependency(db: Session = Depends(get_db)) -> NightModeService:
    return NightModeService(db)


def get_emotion_service_dependency(db: Session = Depends(get_db)) -> EmotionService:
    return EmotionService(db)


def get_rag_service_dependency(db: Session = Depends(get_db)) -> RAGService:
    return RAGService(db)


def get_summary_service_dependency(db: Session = Depends(get_db)) -> SummaryService:
    return SummaryService(db)


def get_notification_service_dependency(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


def get_task_service_dependency(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


def get_schedule_service_dependency(db: Session = Depends(get_db)) -> ScheduleService:
    return ScheduleService(db)


def get_activity_service_dependency(db: Session = Depends(get_db)) -> ActivityService:
    return ActivityService(db)


def get_sync_service_dependency(db: Session = Depends(get_db)) -> SyncService:
    return SyncService(db)


def get_user_service_dependency(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_storage_service_dependency() -> StorageService:
    return StorageService()


def get_voice_service_dependency() -> VoiceService:
    return VoiceService()


def get_family_service_dependency(db: Session = Depends(get_db)) -> FamilyService:
    return FamilyService(db)


def get_family_participation_service_dependency(db: Session = Depends(get_db)) -> FamilyParticipationService:
    return FamilyParticipationService(db)


def get_family_feedback_service_dependency(db: Session = Depends(get_db)) -> FamilyFeedbackService:
    return FamilyFeedbackService(db)


def get_support_service_dependency(db: Session = Depends(get_db)) -> SupportService:
    return SupportService(db)


def get_feedback_service_dependency(db: Session = Depends(get_db)) -> FeedbackService:
    return FeedbackService(db)


def get_analytics_service_dependency(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


def get_monitoring_service_dependency(db: Session = Depends(get_db)) -> MonitoringService:
    return MonitoringService(db)


def get_data_export_service_dependency(db: Session = Depends(get_db)) -> DataExportService:
    return DataExportService(db)


def get_data_deletion_service_dependency(db: Session = Depends(get_db)) -> DataDeletionService:
    return DataDeletionService(db)


def get_help_service_dependency(db: Session = Depends(get_db)) -> HelpService:
    return HelpService(db)


def get_payment_service_dependency(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


def get_api_key_service_dependency(db: Session = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(db)


def get_health_check_service_dependency():
    return get_health_check_service()
