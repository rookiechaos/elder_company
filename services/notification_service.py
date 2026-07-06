"""
Notification Service
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from models.knowledge_models import NotificationDB, FamilyMemberDB
from services.base_service import BaseService
from services.logging_service import logger


class NotificationService(BaseService):
    """Notification service"""
    
    def send_notification(
        self,
        recipient_type: str,
        recipient_id: str,
        notification_type: str,
        title: str,
        content: str,
        related_task_id: Optional[str] = None,
        related_schedule_id: Optional[str] = None,
        related_activity_id: Optional[str] = None,
        delivery_method: str = "in_app"
    ) -> Dict[str, Any]:
        """
        Send notification
        
        Args:
            recipient_type: Recipient type (caregiver, elder, family_member)
            recipient_id: Recipient ID
            notification_type: Notification type (task_reminder, schedule_reminder, emergency, etc.)
            title: Notification title
            content: Notification content
            related_task_id: Related task ID (optional)
            related_schedule_id: Related schedule ID (optional)
            related_activity_id: Related activity ID (optional)
            delivery_method: Delivery method (push, email, sms, in_app)
            
        Returns:
            Created notification
        """
        notification_id = f"notif_{uuid.uuid4().hex[:12]}"
        
        notification = NotificationDB(
            notification_id=notification_id,
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            notification_type=notification_type,
            title=title,
            content=content,
            related_task_id=related_task_id,
            related_schedule_id=related_schedule_id,
            related_activity_id=related_activity_id,
            delivery_method=delivery_method
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.log_info(f"Notification sent: {notification_id} to {recipient_type}:{recipient_id}")
        
        # For reminder types, use AI gentle tone when content is empty or default
        if notification_type in ["task_reminder", "schedule_reminder"] and not content:
            try:
                from services.reminder_service import ReminderService
                
                reminder_text = ReminderService.generate_gentle_reminder(
                    reminder_type=notification_type.replace("_reminder", ""),
                    task_title=title if notification_type == "task_reminder" else None,
                    schedule_title=title if notification_type == "schedule_reminder" else None
                )
                
                if reminder_text:
                    notification.content = reminder_text
                    self.db.commit()
            except Exception as e:
                logger.log_warning(f"Failed to generate AI reminder: {e}")
        
        # Deliver notification per delivery_method
        self._deliver_notification(notification, delivery_method)
        
        return self._notification_to_dict(notification)
    
    def _deliver_notification(self, notification: NotificationDB, delivery_method: str):
        """
        Deliver notification
        
        Args:
            notification: Notification object
            delivery_method: Delivery method
        """
        try:
            if delivery_method == "push":
                # Get device token
                device_token = self._get_device_token(notification.recipient_id, notification.recipient_type)
                if device_token:
                    from services.push_service import get_push_service
                    push_service = get_push_service()
                    push_service.send_push_notification(
                        device_token=device_token,
                        title=notification.title,
                        body=notification.content,
                        data={
                            "notification_id": notification.notification_id,
                            "notification_type": notification.notification_type,
                            "related_task_id": notification.related_task_id,
                            "related_schedule_id": notification.related_schedule_id
                        }
                    )
                
            elif delivery_method == "email":
                # Get email address
                email = self._get_user_email(notification.recipient_id, notification.recipient_type)
                if email:
                    from services.email_service import get_email_service
                    email_service = get_email_service()
                    email_service.send_email(
                        to_email=email,
                        subject=notification.title,
                        body=notification.content
                    )
                
            elif delivery_method == "sms":
                # Get phone number
                phone = self._get_user_phone(notification.recipient_id, notification.recipient_type)
                if phone:
                    from services.sms_service import get_sms_service
                    sms_service = get_sms_service()
                    sms_service.send_sms(
                        to_phone=phone,
                        message=f"{notification.title}: {notification.content}"
                    )
                
            # in_app notifications are stored in DB; no extra delivery
            
        except Exception as e:
            logger.log_warning(f"Failed to deliver notification via {delivery_method}: {e}")
    
    def _get_device_token(self, recipient_id: str, recipient_type: str) -> Optional[str]:
        """Get device push token"""
        try:
            from models.auth_models import DeviceDB
            
            # Get device by recipient type
            if recipient_type == "caregiver" or recipient_type == "elder":
                # Get user's primary device
                device = self.db.query(DeviceDB).filter(
                    DeviceDB.user_id == recipient_id,
                    DeviceDB.is_active == True,
                    DeviceDB.push_token.isnot(None)
                ).order_by(DeviceDB.is_primary.desc()).first()
                
                if device and device.push_token:
                    return device.push_token
            
            elif recipient_type == "family_member":
                # Family member: resolve linked elder ID then device
                from models.knowledge_models import FamilyMemberDB
                member = self.db.query(FamilyMemberDB).filter(
                    FamilyMemberDB.member_id == recipient_id
                ).first()
                
                if member:
                    # Get elder's device (family may have none)
                    device = self.db.query(DeviceDB).filter(
                        DeviceDB.user_id == member.elder_id,
                        DeviceDB.is_active == True,
                        DeviceDB.push_token.isnot(None)
                    ).order_by(DeviceDB.is_primary.desc()).first()
                    
                    if device and device.push_token:
                        return device.push_token
            
            return None
        except Exception as e:
            logger.log_warning(f"Failed to get device token: {e}")
            return None
    
    def _get_user_email(self, recipient_id: str, recipient_type: str) -> Optional[str]:
        """Get user email address"""
        try:
            if recipient_type == "caregiver" or recipient_type == "elder":
                from models.auth_models import UserAuthDB
                user = self.db.query(UserAuthDB).filter(
                    UserAuthDB.user_id == recipient_id
                ).first()
                
                if user and user.email:
                    return user.email
            
            elif recipient_type == "family_member":
                from models.knowledge_models import FamilyMemberDB
                member = self.db.query(FamilyMemberDB).filter(
                    FamilyMemberDB.member_id == recipient_id
                ).first()
                
                if member and member.email:
                    return member.email
            
            return None
        except Exception as e:
            logger.log_warning(f"Failed to get user email: {e}")
            return None
    
    def _get_user_phone(self, recipient_id: str, recipient_type: str) -> Optional[str]:
        """Get user phone number"""
        try:
            if recipient_type == "caregiver" or recipient_type == "elder":
                from models.auth_models import UserAuthDB
                user = self.db.query(UserAuthDB).filter(
                    UserAuthDB.user_id == recipient_id
                ).first()
                
                if user and user.phone:
                    return user.phone
            
            elif recipient_type == "family_member":
                from models.knowledge_models import FamilyMemberDB
                member = self.db.query(FamilyMemberDB).filter(
                    FamilyMemberDB.member_id == recipient_id
                ).first()
                
                if member and member.phone:
                    return member.phone
            
            return None
        except Exception as e:
            logger.log_warning(f"Failed to get user phone: {e}")
            return None
    
    def send_family_notification(
        self,
        elder_id: str,
        notification_type: str,
        title: str,
        content: str,
        related_task_id: Optional[str] = None,
        related_schedule_id: Optional[str] = None,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Send notification to family members
        
        Args:
            elder_id: Elder ID
            notification_type: Notification type
            title: Notification title
            content: Notification content
            related_task_id: Related task ID (optional)
            related_schedule_id: Related schedule ID (optional)
            org_id: Organization ID (optional)
            
        Returns:
            List of sent notifications
        """
        # Get family member list
        query = self.db.query(FamilyMemberDB).filter(
            and_(
                FamilyMemberDB.elder_id == elder_id,
                FamilyMemberDB.is_active == True
            )
        )
        
        if org_id:
            query = query.filter(FamilyMemberDB.org_id == org_id)
        
        family_members = query.all()
        
        notifications = []
        
        for member in family_members:
            # Check notification preferences
            prefs = member.notification_preferences or {}
            
            # Check whether this notification type should be sent
            should_send = False
            if notification_type == "task_reminder" and prefs.get("tasks", True):
                should_send = True
            elif notification_type == "schedule_reminder" and prefs.get("schedules", True):
                should_send = True
            elif notification_type == "emergency" and prefs.get("emergency", True):
                should_send = True
            elif notification_type == "activity" and prefs.get("activities", True):
                should_send = True
            elif notification_type not in ["task_reminder", "schedule_reminder", "emergency", "activity"]:
                should_send = True  # Other types sent by default
            
            if should_send:
                notification = self.send_notification(
                    recipient_type="family_member",
                    recipient_id=member.member_id,
                    notification_type=notification_type,
                    title=title,
                    content=content,
                    related_task_id=related_task_id,
                    related_schedule_id=related_schedule_id,
                    delivery_method="in_app"  # May follow member preference
                )
                notifications.append(notification)
        
        return notifications
    
    def get_notifications(
        self,
        recipient_id: str,
        recipient_type: Optional[str] = None,
        is_read: Optional[bool] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notification list
        
        Args:
            recipient_id: Recipient ID
            recipient_type: Recipient type (optional)
            is_read: Read flag (optional)
            limit: Result limit
            
        Returns:
            Notification list
        """
        query = self.db.query(NotificationDB).filter(
            NotificationDB.recipient_id == recipient_id
        )
        
        if recipient_type:
            query = query.filter(NotificationDB.recipient_type == recipient_type)
        if is_read is not None:
            query = query.filter(NotificationDB.is_read == is_read)
        
        notifications = query.order_by(desc(NotificationDB.created_at)).limit(limit).all()
        
        return [self._notification_to_dict(notif) for notif in notifications]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Whether mark succeeded
        """
        notification = self.db.query(NotificationDB).filter(
            NotificationDB.notification_id == notification_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = utc_now()
        
        self.db.commit()
        
        return True
    
    def mark_all_as_read(self, recipient_id: str) -> int:
        """
        Mark all notifications as read
        
        Args:
            recipient_id: Recipient ID
            
        Returns:
            Number marked
        """
        notifications = self.db.query(NotificationDB).filter(
            and_(
                NotificationDB.recipient_id == recipient_id,
                NotificationDB.is_read == False
            )
        ).all()
        
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = utc_now()
            count += 1
        
        self.db.commit()
        
        return count
    
    def _notification_to_dict(self, notification: NotificationDB) -> Dict[str, Any]:
        """Convert notification to dict"""
        return {
            "notification_id": notification.notification_id,
            "recipient_type": notification.recipient_type,
            "recipient_id": notification.recipient_id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "content": notification.content,
            "related_task_id": notification.related_task_id,
            "related_schedule_id": notification.related_schedule_id,
            "related_activity_id": notification.related_activity_id,
            "is_read": notification.is_read,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
            "delivery_method": notification.delivery_method,
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        }


def get_notification_service(db: Session) -> NotificationService:
    """Get notification service instance"""
    return NotificationService(db)
