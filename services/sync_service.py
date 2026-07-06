"""
Sync Service - Cloud data synchronization
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
import json

from models.auth_models import SyncLogDB, DataVersionDB, DeviceDB
from models.database import (
    UserProfileDB, ActivityRecordDB, TranslationHistoryDB
)
from services.user_service import UserService
from services.activity_service import ActivityService
from services.base_service import BaseService


class SyncService(BaseService):
    """Service for cloud data synchronization"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.user_service = UserService(db)
        self.activity_service = ActivityService(db)
    
    def sync_user_profile(
        self,
        user_id: str,
        device_id: str,
        local_data: Dict[str, Any],
        sync_type: str = "incremental"
    ) -> Dict[str, Any]:
        """Sync user profile data"""
        
        # Get server version
        server_profile = self.user_service.get_user_profile(user_id)
        
        # Check for conflicts
        conflict = self._check_conflict(
            user_id, "profile", user_id, 
            local_data.get("updated_at"), 
            server_profile.get("updated_at")
        )
        
        if conflict:
            # Conflict resolution: server wins by default, but can be customized
            resolution = "server_wins"
            synced_data = server_profile
        else:
            # Merge data (local updates take precedence if newer)
            synced_data = self._merge_profile_data(server_profile, local_data)
            self.user_service.update_user_profile(user_id, synced_data)
            resolution = "merged"
        
        # Update device sync time
        self._update_device_sync(device_id)
        
        # Log sync
        self._log_sync(
            user_id, device_id, "profile", sync_type,
            records_synced=1,
            records_conflicted=1 if conflict else 0
        )
        
        return {
            "data_type": "profile",
            "synced_data": synced_data,
            "conflict": conflict,
            "resolution": resolution
        }
    
    def sync_activity_records(
        self,
        user_id: str,
        device_id: str,
        local_records: List[Dict[str, Any]],
        sync_type: str = "incremental"
    ) -> Dict[str, Any]:
        """Sync activity records"""
        
        # Get server records
        server_records = self.activity_service.get_activity_records(
            caregiver_id=user_id,
            limit=1000
        )
        
        # Create lookup
        server_lookup = {r["record_id"]: r for r in server_records}
        
        synced_count = 0
        conflict_count = 0
        new_records = []
        
        for local_record in local_records:
            record_id = local_record.get("record_id")
            
            if not record_id:
                # New record, create on server
                try:
                    new_record = self.activity_service.create_activity_record(
                        caregiver_id=user_id,
                        activity_data=local_record,
                        org_id=local_record.get("org_id")
                    )
                    new_records.append(new_record)
                    synced_count += 1
                except Exception as e:
                    conflict_count += 1
            else:
                # Existing record, check for conflicts
                server_record = server_lookup.get(record_id)
                
                if not server_record:
                    # Record doesn't exist on server, create it
                    try:
                        new_record = self.activity_service.create_activity_record(
                            caregiver_id=user_id,
                            activity_data=local_record,
                            org_id=local_record.get("org_id")
                        )
                        synced_count += 1
                    except Exception as e:
                        conflict_count += 1
                else:
                    # Check for conflict
                    conflict = self._check_conflict(
                        user_id, "activity_record", record_id,
                        local_record.get("updated_at"),
                        server_record.get("created_at")
                    )
                    
                    if conflict:
                        conflict_count += 1
                    else:
                        # Update if local is newer
                        if self._is_newer(local_record.get("updated_at"), server_record.get("created_at")):
                            # Update logic here
                            synced_count += 1
        
        # Get updated records from server
        updated_records = self.activity_service.get_activity_records(
            caregiver_id=user_id,
            limit=1000
        )
        
        # Log sync
        self._log_sync(
            user_id, device_id, "activities", sync_type,
            records_synced=synced_count,
            records_conflicted=conflict_count
        )
        
        return {
            "data_type": "activities",
            "synced_count": synced_count,
            "conflict_count": conflict_count,
            "new_records": new_records,
            "updated_records": updated_records
        }
    
    def sync_translation_history(
        self,
        user_id: str,
        device_id: str,
        local_history: List[Dict[str, Any]],
        sync_type: str = "incremental"
    ) -> Dict[str, Any]:
        """Sync translation history"""
        
        # Get server history
        server_history = self.user_service.get_translation_history(user_id, limit=1000)
        
        server_lookup = {h.get("id"): h for h in server_history}
        
        synced_count = 0
        new_items = []
        
        for local_item in local_history:
            item_id = local_item.get("id")
            
            if not item_id or item_id not in server_lookup:
                # New item, save to server
                try:
                    self.user_service.save_translation_history(
                        user_id=user_id,
                        original_text=local_item.get("original_text", ""),
                        translated_text=local_item.get("translated_text", ""),
                        source_language=local_item.get("source_language", "ja"),
                        target_language=local_item.get("target_language", "zh"),
                        context=local_item.get("context"),
                        org_id=local_item.get("org_id")
                    )
                    synced_count += 1
                except Exception:
                    pass
        
        # Get updated history
        updated_history = self.user_service.get_translation_history(user_id, limit=1000)
        
        # Log sync
        self._log_sync(
            user_id, device_id, "translations", sync_type,
            records_synced=synced_count
        )
        
        return {
            "data_type": "translations",
            "synced_count": synced_count,
            "updated_history": updated_history
        }
    
    def full_sync(
        self,
        user_id: str,
        device_id: str,
        local_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform full synchronization"""
        
        results = {}
        
        # Sync profile
        if "profile" in local_data:
            results["profile"] = self.sync_user_profile(
                user_id, device_id, local_data["profile"], "full"
            )
        
        # Sync activities
        if "activities" in local_data:
            results["activities"] = self.sync_activity_records(
                user_id, device_id, local_data["activities"], "full"
            )
        
        # Sync translations
        if "translations" in local_data:
            results["translations"] = self.sync_translation_history(
                user_id, device_id, local_data["translations"], "full"
            )
        
        return {
            "sync_type": "full",
            "results": results,
            "timestamp": utc_now().isoformat()
        }
    
    def get_sync_status(self, user_id: str, device_id: str) -> Dict[str, Any]:
        """Get synchronization status"""
        
        device = self.db.query(DeviceDB).filter(
            DeviceDB.device_id == device_id
        ).first()
        
        if not device:
            return {"status": "device_not_found"}
        
        # Get last sync log
        last_sync = self.db.query(SyncLogDB).filter(
            and_(
                SyncLogDB.user_id == user_id,
                SyncLogDB.device_id == device_id
            )
        ).order_by(SyncLogDB.sync_started_at.desc()).first()
        
        return {
            "device_id": device_id,
            "last_sync_at": device.last_sync_at.isoformat() if device.last_sync_at else None,
            "sync_status": device.sync_status,
            "last_sync_result": {
                "status": last_sync.status if last_sync else None,
                "records_synced": last_sync.records_synced if last_sync else 0,
                "sync_completed_at": last_sync.sync_completed_at.isoformat() if last_sync and last_sync.sync_completed_at else None
            } if last_sync else None
        }
    
    def _check_conflict(
        self,
        user_id: str,
        data_type: str,
        data_id: str,
        local_timestamp: Optional[str],
        server_timestamp: Optional[str]
    ) -> bool:
        """Check if there's a data conflict"""
        
        if not local_timestamp or not server_timestamp:
            return False
        
        # Parse timestamps
        try:
            local_dt = datetime.fromisoformat(local_timestamp.replace('Z', '+00:00'))
            server_dt = datetime.fromisoformat(server_timestamp.replace('Z', '+00:00'))
            
            # Conflict if both were modified and timestamps are close (within 1 second)
            time_diff = abs((local_dt - server_dt).total_seconds())
            return time_diff < 1.0 and local_dt != server_dt
        except:
            return False
    
    def _is_newer(self, timestamp1: Optional[str], timestamp2: Optional[str]) -> bool:
        """Check if timestamp1 is newer than timestamp2"""
        if not timestamp1 or not timestamp2:
            return False
        
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(timestamp2.replace('Z', '+00:00'))
            return dt1 > dt2
        except:
            return False
    
    def _merge_profile_data(
        self,
        server_data: Dict[str, Any],
        local_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge server and local profile data"""
        merged = server_data.copy()
        
        # Local data takes precedence for most fields
        for key, value in local_data.items():
            if key not in ["user_id", "created_at"]:  # Don't overwrite these
                merged[key] = value
        
        # Update timestamp
        merged["updated_at"] = utc_now().isoformat()
        
        return merged
    
    def _update_device_sync(self, device_id: str):
        """Update device last sync time"""
        device = self.db.query(DeviceDB).filter(
            DeviceDB.device_id == device_id
        ).first()
        
        if device:
            device.last_sync_at = utc_now()
            device.sync_status = "active"
            device.last_seen_at = utc_now()
            self.safe_commit("sync_user_profile")
    
    def _log_sync(
        self,
        user_id: str,
        device_id: str,
        data_type: str,
        sync_type: str,
        records_synced: int = 0,
        records_conflicted: int = 0,
        status: str = "success"
    ):
        """Log synchronization"""
        sync_id = f"sync_{uuid.uuid4().hex[:12]}"
        
        sync_log = SyncLogDB(
            sync_id=sync_id,
            user_id=user_id,
            device_id=device_id,
            sync_type=sync_type,
            data_type=data_type,
            records_synced=records_synced,
            records_conflicted=records_conflicted,
            status=status,
            sync_completed_at=utc_now()
        )
        
        self.db.add(sync_log)
        self.safe_commit("log_sync_operation")
