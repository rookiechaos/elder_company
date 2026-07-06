"""
Data Deletion Service - GDPR compliant account deletion
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.auth_models import UserAuthDB, DeviceDB, ApiKeyDB
from models.database import (
    UserProfileDB, OrganizationDB, TranslationHistoryDB,
    UsageStatisticsDB
)
from models.customer_models import (
    CustomerDB, CaregiverProfileDB, ElderProfileDB,
    CareRelationshipDB, PersonalizationDataDB,
    InteractionHistoryDB
)
from models.feedback_models import FeedbackDB, FeedbackCommentDB
from models.help_models import HelpFeedbackDB


class DataDeletionService:
    """Service for GDPR compliant data deletion"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def delete_user_account(
        self,
        user_id: str,
        confirmation_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete user account and all associated data (GDPR compliant)
        
        Args:
            user_id: User ID to delete
            confirmation_token: Optional confirmation token for security
        
        Returns:
            Dict with deletion summary
        """
        deletion_log = {
            "user_id": user_id,
            "deleted_at": utc_now().isoformat(),
            "deleted_items": {}
        }
        
        try:
            # 1. Delete API keys
            api_keys = self.db.query(ApiKeyDB).filter(
                ApiKeyDB.user_id == user_id
            ).all()
            api_key_count = len(api_keys)
            for key in api_keys:
                self.db.delete(key)
            deletion_log["deleted_items"]["api_keys"] = api_key_count
            
            # 2. Delete devices
            devices = self.db.query(DeviceDB).filter(
                DeviceDB.user_id == user_id
            ).all()
            device_count = len(devices)
            for device in devices:
                self.db.delete(device)
            deletion_log["deleted_items"]["devices"] = device_count
            
            # 3. Delete translation history
            translations = self.db.query(TranslationHistoryDB).filter(
                TranslationHistoryDB.user_id == user_id
            ).all()
            translation_count = len(translations)
            for translation in translations:
                self.db.delete(translation)
            deletion_log["deleted_items"]["translations"] = translation_count
            
            # 4. Delete usage statistics
            stats = self.db.query(UsageStatisticsDB).filter(
                UsageStatisticsDB.user_id == user_id
            ).all()
            stats_count = len(stats)
            for stat in stats:
                self.db.delete(stat)
            deletion_log["deleted_items"]["usage_statistics"] = stats_count
            
            # 5. Delete customer/elder profiles
            # Delete caregiver profile
            caregiver = self.db.query(CaregiverProfileDB).filter(
                CaregiverProfileDB.caregiver_id == user_id
            ).first()
            if caregiver:
                # Delete relationships
                relationships = self.db.query(CareRelationshipDB).filter(
                    CareRelationshipDB.caregiver_id == user_id
                ).all()
                relationship_count = len(relationships)
                for rel in relationships:
                    self.db.delete(rel)
                deletion_log["deleted_items"]["care_relationships"] = relationship_count
                
                # Delete interaction history
                interactions = self.db.query(InteractionHistoryDB).filter(
                    InteractionHistoryDB.caregiver_id == user_id
                ).all()
                interaction_count = len(interactions)
                for interaction in interactions:
                    self.db.delete(interaction)
                deletion_log["deleted_items"]["interactions"] = interaction_count
                
                self.db.delete(caregiver)
                deletion_log["deleted_items"]["caregiver_profile"] = 1
            
            # 6. Delete personalization data
            # PersonalizationDataDB uses customer_id, not user_id
            customer = self.db.query(CustomerDB).filter(
                CustomerDB.user_id == user_id
            ).first()
            if customer:
                personalization = self.db.query(PersonalizationDataDB).filter(
                    PersonalizationDataDB.customer_id == customer.customer_id
                ).all()
                personalization_count = len(personalization)
                for p in personalization:
                    self.db.delete(p)
                deletion_log["deleted_items"]["personalization"] = personalization_count
            else:
                deletion_log["deleted_items"]["personalization"] = 0
            
            # 7. Delete feedback (anonymize instead of delete for support purposes)
            feedbacks = self.db.query(FeedbackDB).filter(
                FeedbackDB.user_id == user_id
            ).all()
            feedback_count = len(feedbacks)
            for feedback in feedbacks:
                # Anonymize instead of delete
                feedback.user_id = None
                feedback.contact_email = None
                feedback.contact_phone = None
                feedback.ip_address = None
            deletion_log["deleted_items"]["feedback_anonymized"] = feedback_count
            
            # 8. Delete help feedback
            help_feedback = self.db.query(HelpFeedbackDB).filter(
                HelpFeedbackDB.user_id == user_id
            ).all()
            help_feedback_count = len(help_feedback)
            for hf in help_feedback:
                hf.user_id = None
            deletion_log["deleted_items"]["help_feedback_anonymized"] = help_feedback_count
            
            # 9. Delete user profile
            profile = self.db.query(UserProfileDB).filter(
                UserProfileDB.user_id == user_id
            ).first()
            if profile:
                self.db.delete(profile)
                deletion_log["deleted_items"]["user_profile"] = 1
            
            # 10. Delete authentication (last, as it's the main record)
            auth = self.db.query(UserAuthDB).filter(
                UserAuthDB.user_id == user_id
            ).first()
            if auth:
                self.db.delete(auth)
                deletion_log["deleted_items"]["authentication"] = 1
            
            # Commit all deletions
            self.db.commit()
            
            deletion_log["status"] = "success"
            deletion_log["message"] = "Account and all associated data deleted successfully"
            
            return deletion_log
            
        except Exception as e:
            self.db.rollback()
            deletion_log["status"] = "error"
            deletion_log["error"] = str(e)
            raise
    
    def request_account_deletion(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Request account deletion (creates a deletion request)
        In production, this might send a confirmation email
        """
        return {
            "user_id": user_id,
            "requested_at": utc_now().isoformat(),
            "status": "pending",
            "message": "Account deletion requested. Please confirm to proceed.",
            "confirmation_required": True
        }
    
    def get_deletion_summary(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get summary of data that will be deleted"""
        summary = {
            "user_id": user_id,
            "data_types": {}
        }
        
        # Count items
        summary["data_types"]["api_keys"] = self.db.query(ApiKeyDB).filter(
            ApiKeyDB.user_id == user_id
        ).count()
        
        summary["data_types"]["devices"] = self.db.query(DeviceDB).filter(
            DeviceDB.user_id == user_id
        ).count()
        
        summary["data_types"]["translations"] = self.db.query(TranslationHistoryDB).filter(
            TranslationHistoryDB.user_id == user_id
        ).count()
        
        summary["data_types"]["usage_statistics"] = self.db.query(UsageStatisticsDB).filter(
            UsageStatisticsDB.user_id == user_id
        ).count()
        
        # PersonalizationDataDB uses customer_id, not user_id
        # Need to find customer_id from CustomerDB first
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.user_id == user_id
        ).first()
        if customer:
            summary["data_types"]["personalization"] = self.db.query(PersonalizationDataDB).filter(
                PersonalizationDataDB.customer_id == customer.customer_id
            ).count()
        else:
            summary["data_types"]["personalization"] = 0
        
        summary["data_types"]["interactions"] = self.db.query(InteractionHistoryDB).filter(
            InteractionHistoryDB.caregiver_id == user_id
        ).count()
        
        summary["data_types"]["care_relationships"] = self.db.query(CareRelationshipDB).filter(
            CareRelationshipDB.caregiver_id == user_id
        ).count()
        
        summary["total_items"] = sum(summary["data_types"].values())
        
        return summary


def get_data_deletion_service(db: Session) -> DataDeletionService:
    """Get data deletion service instance"""
    return DataDeletionService(db)
