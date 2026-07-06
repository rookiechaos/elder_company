"""
Support Service - Support ticket management
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from models.support_models import SupportTicketDB, TicketMessageDB, TicketActivityDB


class SupportService:
    """Service for support ticket management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_ticket(
        self,
        user_id: Optional[str],
        org_id: Optional[str],
        subject: str,
        description: str,
        category: str,
        subcategory: Optional[str] = None,
        priority: str = "normal",
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new support ticket"""
        ticket_id = f"ticket_{uuid.uuid4().hex[:12]}"
        
        ticket = SupportTicketDB(
            ticket_id=ticket_id,
            user_id=user_id,
            org_id=org_id,
            subject=subject,
            description=description,
            category=category,
            subcategory=subcategory,
            priority=priority,
            attachments=attachments or [],
            status="open"
        )
        
        self.db.add(ticket)
        
        # Create activity log
        self._log_activity(ticket_id, user_id, "created", {"subject": subject})
        
        self.db.commit()
        self.db.refresh(ticket)
        
        return self._ticket_to_dict(ticket)
    
    def get_ticket(
        self,
        ticket_id: str,
        user_id: Optional[str] = None,
        include_messages: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get a single ticket"""
        query = self.db.query(SupportTicketDB).filter(
            SupportTicketDB.ticket_id == ticket_id
        )
        
        # Users can only see their own tickets unless admin
        if user_id:
            query = query.filter(
                or_(
                    SupportTicketDB.user_id == user_id,
                    SupportTicketDB.assigned_to == user_id  # Assigned support staff
                )
            )
        
        ticket = query.first()
        
        if not ticket:
            return None
        
        result = self._ticket_to_dict(ticket)
        
        if include_messages:
            # Get messages
            messages = self.db.query(TicketMessageDB).filter(
                and_(
                    TicketMessageDB.ticket_id == ticket_id,
                    TicketMessageDB.is_internal == False  # Only non-internal messages
                )
            ).order_by(TicketMessageDB.created_at.asc()).all()
            
            result["messages"] = [self._message_to_dict(m) for m in messages]
            
            # Get activity log
            activities = self.db.query(TicketActivityDB).filter(
                TicketActivityDB.ticket_id == ticket_id
            ).order_by(TicketActivityDB.created_at.asc()).all()
            
            result["activities"] = [self._activity_to_dict(a) for a in activities]
        
        return result
    
    def list_tickets(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List tickets with filters"""
        query = self.db.query(SupportTicketDB)
        
        if user_id:
            query = query.filter(SupportTicketDB.user_id == user_id)
        
        if org_id:
            query = query.filter(SupportTicketDB.org_id == org_id)
        
        if status:
            query = query.filter(SupportTicketDB.status == status)
        
        if category:
            query = query.filter(SupportTicketDB.category == category)
        
        if priority:
            query = query.filter(SupportTicketDB.priority == priority)
        
        if assigned_to:
            query = query.filter(SupportTicketDB.assigned_to == assigned_to)
        
        total = query.count()
        
        tickets = query.order_by(
            desc(SupportTicketDB.created_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "tickets": [self._ticket_to_dict(t) for t in tickets],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        resolution: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update ticket (admin/support staff)"""
        ticket = self.db.query(SupportTicketDB).filter(
            SupportTicketDB.ticket_id == ticket_id
        ).first()
        
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        changes = {}
        
        if status and status != ticket.status:
            old_status = ticket.status
            ticket.status = status
            changes["status"] = {"old": old_status, "new": status}
            
            if status == "resolved":
                ticket.resolved_at = utc_now()
                ticket.resolved_by = updated_by
                if resolution:
                    ticket.resolution = resolution
            self._log_activity(ticket_id, updated_by, "status_changed", changes["status"])
        
        if priority and priority != ticket.priority:
            old_priority = ticket.priority
            ticket.priority = priority
            changes["priority"] = {"old": old_priority, "new": priority}
            self._log_activity(ticket_id, updated_by, "priority_changed", changes["priority"])
        
        if assigned_to and assigned_to != ticket.assigned_to:
            old_assigned = ticket.assigned_to
            ticket.assigned_to = assigned_to
            ticket.assigned_at = utc_now()
            changes["assigned"] = {"old": old_assigned, "new": assigned_to}
            self._log_activity(ticket_id, updated_by, "assigned", changes["assigned"])
        
        if resolution and not ticket.resolution:
            ticket.resolution = resolution
            changes["resolution"] = True
        
        ticket.updated_at = utc_now()
        
        if changes:
            self._log_activity(ticket_id, updated_by, "updated", changes)
        
        self.db.commit()
        self.db.refresh(ticket)
        
        return self._ticket_to_dict(ticket)
    
    def add_message(
        self,
        ticket_id: str,
        user_id: Optional[str],
        content: str,
        is_admin: bool = False,
        is_internal: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a message to ticket"""
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        
        message = TicketMessageDB(
            message_id=message_id,
            ticket_id=ticket_id,
            user_id=user_id,
            is_admin=is_admin,
            is_internal=is_internal,
            content=content,
            attachments=attachments or []
        )
        
        self.db.add(message)
        
        # Update ticket
        ticket = self.db.query(SupportTicketDB).filter(
            SupportTicketDB.ticket_id == ticket_id
        ).first()
        
        if ticket:
            if not ticket.first_response_at and is_admin:
                ticket.first_response_at = utc_now()
            ticket.last_response_at = utc_now()
            ticket.updated_at = utc_now()
        
        self._log_activity(ticket_id, user_id, "message_added", {"is_admin": is_admin})
        
        self.db.commit()
        self.db.refresh(message)
        
        return self._message_to_dict(message)
    
    def _log_activity(
        self,
        ticket_id: str,
        user_id: Optional[str],
        activity_type: str,
        activity_data: Optional[Dict[str, Any]] = None
    ):
        """Log ticket activity"""
        activity_id = f"activity_{uuid.uuid4().hex[:12]}"
        
        activity = TicketActivityDB(
            activity_id=activity_id,
            ticket_id=ticket_id,
            user_id=user_id,
            activity_type=activity_type,
            activity_data=activity_data or {}
        )
        
        self.db.add(activity)
    
    def _ticket_to_dict(self, ticket: SupportTicketDB) -> Dict[str, Any]:
        """Convert ticket to dictionary"""
        return {
            "ticket_id": ticket.ticket_id,
            "user_id": ticket.user_id,
            "org_id": ticket.org_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category,
            "subcategory": ticket.subcategory,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_to": ticket.assigned_to,
            "assigned_at": ticket.assigned_at.isoformat() if ticket.assigned_at else None,
            "resolution": ticket.resolution,
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            "resolved_by": ticket.resolved_by,
            "attachments": ticket.attachments or [],
            "tags": ticket.tags or [],
            "first_response_at": ticket.first_response_at.isoformat() if ticket.first_response_at else None,
            "last_response_at": ticket.last_response_at.isoformat() if ticket.last_response_at else None,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None
        }
    
    def _message_to_dict(self, message: TicketMessageDB) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": message.message_id,
            "ticket_id": message.ticket_id,
            "user_id": message.user_id,
            "is_admin": message.is_admin,
            "is_internal": message.is_internal,
            "content": message.content,
            "attachments": message.attachments or [],
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
    
    def _activity_to_dict(self, activity: TicketActivityDB) -> Dict[str, Any]:
        """Convert activity to dictionary"""
        return {
            "activity_id": activity.activity_id,
            "ticket_id": activity.ticket_id,
            "user_id": activity.user_id,
            "activity_type": activity.activity_type,
            "activity_data": activity.activity_data or {},
            "created_at": activity.created_at.isoformat() if activity.created_at else None
        }


def get_support_service(db: Session) -> SupportService:
    """Get support service instance"""
    return SupportService(db)
