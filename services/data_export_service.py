"""
Data Export Service - GDPR compliant data export
"""

import json
import csv
import io
from typing import Dict, Any, List, Optional
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
from services.base_service import BaseService


class DataExportService(BaseService):
    """Service for exporting user data (GDPR compliant)"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def export_user_data(
        self,
        user_id: str,
        format: str = "json"  # json or csv
    ) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance
        
        Args:
            user_id: User ID to export data for
            format: Export format (json or csv)
        
        Returns:
            Dict with export data and metadata
        """
        export_data = {
            "user_id": user_id,
            "exported_at": utc_now().isoformat(),
            "format": format,
            "data": {}
        }
        
        # 1. User authentication data
        auth_data = self._export_auth_data(user_id)
        export_data["data"]["authentication"] = auth_data
        
        # 2. User profile data
        profile_data = self._export_profile_data(user_id)
        export_data["data"]["profile"] = profile_data
        
        # 3. Translation history
        translation_data = self._export_translation_history(user_id)
        export_data["data"]["translations"] = translation_data
        
        # 4. Customer/elder profiles
        customer_data = self._export_customer_data(user_id)
        export_data["data"]["customers"] = customer_data
        
        # 5. Devices
        device_data = self._export_device_data(user_id)
        export_data["data"]["devices"] = device_data
        
        # 6. API keys
        api_key_data = self._export_api_keys(user_id)
        export_data["data"]["api_keys"] = api_key_data
        
        # 7. Personalization data
        personalization_data = self._export_personalization_data(user_id)
        export_data["data"]["personalization"] = personalization_data
        
        # 8. Interaction history
        interaction_data = self._export_interaction_history(user_id)
        export_data["data"]["interactions"] = interaction_data
        
        # Convert to requested format
        if format == "csv":
            export_data["csv_data"] = self._convert_to_csv(export_data["data"])
        
        # Add metadata
        export_data["metadata"] = {
            "total_records": self._count_total_records(export_data["data"]),
            "export_version": "1.0",
            "compliance": "GDPR"
        }
        
        return export_data
    
    def _export_auth_data(self, user_id: str) -> Dict[str, Any]:
        """Export authentication data"""
        auth = self.db.query(UserAuthDB).filter(
            UserAuthDB.user_id == user_id
        ).first()
        
        if not auth:
            return {}
        
        return {
            "user_id": auth.user_id,
            "email": auth.email,
            "phone": auth.phone,
            "username": auth.username,
            "auth_method": auth.auth_method,
            "is_email_verified": auth.is_email_verified,
            "is_phone_verified": auth.is_phone_verified,
            "is_active": auth.is_active,
            "last_login": auth.last_login.isoformat() if auth.last_login else None,
            "created_at": auth.created_at.isoformat() if auth.created_at else None
        }
    
    def _export_profile_data(self, user_id: str) -> Dict[str, Any]:
        """Export user profile data"""
        profile = self.db.query(UserProfileDB).filter(
            UserProfileDB.user_id == user_id
        ).first()
        
        if not profile:
            return {}
        
        return {
            "user_id": profile.user_id,
            "org_id": profile.org_id,
            "display_name": profile.display_name,
            "language_preference": profile.language_preference,
            "timezone": profile.timezone,
            "custom_terms": profile.custom_terms,
            "translation_style": profile.translation_style,
            "care_scenarios": profile.care_scenarios,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
        }
    
    def _export_translation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Export translation history"""
        translations = self.db.query(TranslationHistoryDB).filter(
            TranslationHistoryDB.user_id == user_id
        ).order_by(TranslationHistoryDB.timestamp.desc()).all()
        
        return [
            {
                "translation_id": t.translation_id,
                "source_text": t.source_text,
                "target_text": t.target_text,
                "source_language": t.source_language,
                "target_language": t.target_language,
                "context": t.context,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None
            }
            for t in translations
        ]
    
    def _export_customer_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Export customer/elder profile data"""
        # Get customer record for this user
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.user_id == user_id
        ).first()
        
        customers = []
        
        if customer:
            # Get caregiver profile
            caregiver = self.db.query(CaregiverProfileDB).filter(
                CaregiverProfileDB.customer_id == customer.customer_id
            ).first()
            
            if caregiver:
                # Get related elder profiles through care relationships
                relationships = self.db.query(CareRelationshipDB).filter(
                    CareRelationshipDB.caregiver_id == customer.customer_id
                ).all()
                
                for rel in relationships:
                    elder_customer = self.db.query(CustomerDB).filter(
                        CustomerDB.customer_id == rel.elder_id
                    ).first()
                    
                    if elder_customer:
                        elder = self.db.query(ElderProfileDB).filter(
                            ElderProfileDB.customer_id == elder_customer.customer_id
                        ).first()
                        
                        if elder:
                            customers.append({
                                "elder_id": elder_customer.customer_id,
                                "name": elder_customer.name,
                                "age": elder_customer.age,
                                "gender": elder_customer.gender,
                                "health_conditions": elder.health_conditions,
                                "interests": elder.interests,
                                "relationship_type": rel.relationship_type,
                                "created_at": elder.created_at.isoformat() if elder.created_at else None
                            })
        
        return customers
    
    def _export_device_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Export device data"""
        devices = self.db.query(DeviceDB).filter(
            DeviceDB.user_id == user_id
        ).all()
        
        return [
            {
                "device_id": d.device_id,
                "device_name": d.device_name,
                "device_type": d.device_type,
                "platform": d.platform,
                "device_model": d.device_model,
                "os_version": d.os_version,
                "app_version": d.app_version,
                "is_primary": d.is_primary,
                "last_sync_at": d.last_sync_at.isoformat() if d.last_sync_at else None,
                "registered_at": d.registered_at.isoformat() if d.registered_at else None
            }
            for d in devices
        ]
    
    def _export_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Export API keys (without actual key values for security)"""
        keys = self.db.query(ApiKeyDB).filter(
            ApiKeyDB.user_id == user_id
        ).all()
        
        return [
            {
                "key_id": k.id,
                "key_name": k.key_name,
                "key_type": k.key_type,
                "is_active": k.is_active,
                "total_requests": k.total_requests,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "created_at": k.created_at.isoformat() if k.created_at else None,
                "expires_at": k.expires_at.isoformat() if k.expires_at else None
                # Note: Actual API key not exported for security
            }
            for k in keys
        ]
    
    def _export_personalization_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Export personalization data"""
        # PersonalizationDataDB uses customer_id, not user_id
        # Need to find customer_id from CustomerDB first
        customer = self.db.query(CustomerDB).filter(
            CustomerDB.user_id == user_id
        ).first()
        
        if not customer:
            return []
        
        personalization = self.db.query(PersonalizationDataDB).filter(
            PersonalizationDataDB.customer_id == customer.customer_id
        ).all()
        
        return [
            {
                "data_id": p.data_id,
                "data_type": p.data_type,
                "preference_data": p.preference_data,
                "source": p.source,
                "confidence_score": p.confidence_score,
                "usage_count": p.usage_count,
                "last_used_at": p.last_used_at.isoformat() if p.last_used_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in personalization
        ]
    
    def _export_interaction_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Export interaction history"""
        interactions = self.db.query(InteractionHistoryDB).filter(
            InteractionHistoryDB.caregiver_id == user_id
        ).order_by(InteractionHistoryDB.interaction_date.desc()).all()
        
        return [
            {
                "interaction_id": i.interaction_id,
                "interaction_type": i.interaction_type,
                "elder_id": i.elder_id,
                "content": i.content,
                "quality_score": i.quality_score,
                "engagement_level": i.engagement_level,
                "satisfaction_score": i.satisfaction_score,
                "elder_mood_before": i.elder_mood_before,
                "elder_mood_after": i.elder_mood_after,
                "interaction_date": i.interaction_date.isoformat() if i.interaction_date else None,
                "duration_minutes": i.duration_minutes
            }
            for i in interactions
        ]
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Convert data to CSV format"""
        csv_data = {}
        
        for section, section_data in data.items():
            if not section_data:
                continue
            
            if isinstance(section_data, list) and len(section_data) > 0:
                # Convert list to CSV
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=section_data[0].keys())
                writer.writeheader()
                writer.writerows(section_data)
                csv_data[section] = output.getvalue()
            elif isinstance(section_data, dict):
                # Convert dict to CSV (single row)
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=section_data.keys())
                writer.writeheader()
                writer.writerow(section_data)
                csv_data[section] = output.getvalue()
        
        return csv_data
    
    def _count_total_records(self, data: Dict[str, Any]) -> int:
        """Count total records in export"""
        count = 0
        for section_data in data.values():
            if isinstance(section_data, list):
                count += len(section_data)
            elif isinstance(section_data, dict) and section_data:
                count += 1
        return count


def get_data_export_service(db: Session) -> DataExportService:
    """Get data export service instance"""
    return DataExportService(db)
