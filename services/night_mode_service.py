"""
Night Mode Service
Manages night mode configuration
"""

from typing import Dict, Any, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
import uuid

from models.emergency_models import NightModeConfigDB
from services.base_service import BaseService
from services.logging_service import logger


class NightModeService(BaseService):
    """Night mode service"""
    
    def get_night_mode_config(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get night mode configuration
        
        Args:
            user_id: User ID
            
        Returns:
            Night mode config if present
        """
        config = self.db.query(NightModeConfigDB).filter(
            NightModeConfigDB.user_id == user_id
        ).first()
        
        if config:
            return self._config_to_dict(config)
        return None
    
    def update_night_mode_config(
        self,
        user_id: str,
        user_type: str,
        enabled: Optional[bool] = None,
        brightness: Optional[str] = None,
        sound_enabled: Optional[bool] = None,
        text_prompts: Optional[bool] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        sound_type: Optional[str] = None,
        volume: Optional[int] = None,
        font_size: Optional[str] = None,
        color_scheme: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update night mode configuration
        
        Args:
            user_id: User ID
            user_type: User type (elder, caregiver)
            enabled: Enabled flag (optional)
            brightness: Brightness (optional)
            sound_enabled: Sound enabled (optional)
            text_prompts: Text prompts enabled (optional)
            start_time: Start time (optional, HH:MM)
            end_time: End time (optional, HH:MM)
            sound_type: Sound type (optional)
            volume: Volume (optional, 0-100)
            font_size: Font size (optional)
            color_scheme: Color scheme (optional)
            org_id: Organization ID (optional)
            
        Returns:
            Updated configuration
        """
        # Find existing configuration
        config = self.db.query(NightModeConfigDB).filter(
            NightModeConfigDB.user_id == user_id
        ).first()
        
        if config:
            # Update existing configuration
            if enabled is not None:
                config.enabled = enabled
            if brightness is not None:
                config.brightness = brightness
            if sound_enabled is not None:
                config.sound_enabled = sound_enabled
            if text_prompts is not None:
                config.text_prompts = text_prompts
            if start_time is not None:
                config.start_time = start_time
            if end_time is not None:
                config.end_time = end_time
            if sound_type is not None:
                config.sound_type = sound_type
            if volume is not None:
                config.volume = max(0, min(100, volume))  # Clamp to 0-100
            if font_size is not None:
                config.font_size = font_size
            if color_scheme is not None:
                config.color_scheme = color_scheme
            if org_id is not None:
                config.org_id = org_id
            
            config.updated_at = utc_now()
        else:
            # Create new configuration
            config_id = f"nightmode_{uuid.uuid4().hex[:12]}"
            config = NightModeConfigDB(
                config_id=config_id,
                user_id=user_id,
                user_type=user_type,
                org_id=org_id,
                enabled=enabled if enabled is not None else False,
                brightness=brightness or "low",
                sound_enabled=sound_enabled if sound_enabled is not None else False,
                text_prompts=text_prompts if text_prompts is not None else True,
                start_time=start_time,
                end_time=end_time,
                sound_type=sound_type,
                volume=volume if volume is not None else 50,
                font_size=font_size or "large",
                color_scheme=color_scheme or "dark"
            )
            self.db.add(config)
        
        self.safe_commit(action="update_night_mode_config")
        self.safe_refresh(config, action="refresh_night_mode_config")
        
        logger.log_info(
            f"Night mode config updated: {user_id}",
            {"user_id": user_id, "enabled": config.enabled}
        )
        
        return self._config_to_dict(config)
    
    def is_night_mode_active(
        self,
        user_id: str
    ) -> bool:
        """
        Check whether night mode is active
        
        Args:
            user_id: User ID
            
        Returns:
            Whether night mode is active
        """
        config = self.db.query(NightModeConfigDB).filter(
            NightModeConfigDB.user_id == user_id
        ).first()
        
        if not config or not config.enabled:
            return False
        
        # If time range is set, check current time
        if config.start_time and config.end_time:
            try:
                from datetime import time as dt_time
                
                current_time = utc_now().time()
                start = dt_time.fromisoformat(config.start_time)
                end = dt_time.fromisoformat(config.end_time)
                
                # Handle overnight ranges (e.g. 22:00-07:00)
                if start > end:
                    # Overnight: current time after start or before end
                    return current_time >= start or current_time <= end
                else:
                    # Same day: current time between start and end
                    return start <= current_time <= end
            except Exception as e:
                logger.log_warning(f"Failed to parse night mode time: {e}")
                return config.enabled
        
        return config.enabled
    
    def _config_to_dict(self, config: NightModeConfigDB) -> Dict[str, Any]:
        """Convert config to dict"""
        return {
            "config_id": config.config_id,
            "user_id": config.user_id,
            "user_type": config.user_type,
            "org_id": config.org_id,
            "enabled": config.enabled,
            "brightness": config.brightness,
            "sound_enabled": config.sound_enabled,
            "text_prompts": config.text_prompts,
            "start_time": config.start_time,
            "end_time": config.end_time,
            "sound_type": config.sound_type,
            "volume": config.volume,
            "font_size": config.font_size,
            "color_scheme": config.color_scheme,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        }


def get_night_mode_service(db: Session) -> NightModeService:
    """Get night mode service instance"""
    return NightModeService(db)
