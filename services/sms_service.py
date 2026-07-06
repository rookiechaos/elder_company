"""
SMS Notification Service
Supports Twilio SMS
"""

from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv

from services.logging_service import logger

load_dotenv()


class SMSService:
    """SMS notification service (Twilio)"""
    
    def __init__(self):
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        self.sms_enabled = bool(self.twilio_account_sid and self.twilio_auth_token and self.twilio_from_number)
        
        if not self.sms_enabled:
            logger.log_warning("Twilio credentials not found. SMS notifications will not work.")
    
    def send_sms(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send SMS
        
        Args:
            to_phone: Recipient phone (E.164, e.g. +819012345678)
            message: SMS message body
            
        Returns:
            Whether send succeeded
        """
        if not self.sms_enabled:
            logger.log_warning("SMS service not enabled. SMS not sent.")
            return False
        
        if not to_phone:
            logger.log_warning("Recipient phone is empty. SMS not sent.")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message_obj = client.messages.create(
                body=message,
                from_=self.twilio_from_number,
                to=to_phone
            )
            
            if message_obj.sid:
                logger.log_info(f"SMS sent successfully to {to_phone} (SID: {message_obj.sid})")
                return True
            else:
                logger.log_warning(f"SMS sending failed: {message_obj}")
                return False
                
        except ImportError:
            logger.log_warning("twilio library not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logger.log_error(e, {"action": "send_sms", "to_phone": to_phone})
            return False
    
    def send_sms_batch(
        self,
        to_phones: List[str],
        message: str
    ) -> Dict[str, bool]:
        """
        Send SMS in batch
        
        Args:
            to_phones: Recipient phone list
            message: SMS message body
            
        Returns:
            Send results dict {phone: success}
        """
        results = {}
        
        for phone in to_phones:
            success = self.send_sms(phone, message)
            results[phone] = success
        
        return results


# Global instance
_sms_service: Optional[SMSService] = None


def get_sms_service() -> SMSService:
    """Get SMS service instance (singleton)"""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
