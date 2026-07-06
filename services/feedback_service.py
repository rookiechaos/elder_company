"""
Feedback Service - User feedback management
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from models.feedback_models import FeedbackDB, FeedbackCommentDB, SatisfactionSurveyDB


class FeedbackService:
    """Service for feedback management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_feedback(
        self,
        user_id: Optional[str],
        org_id: Optional[str],
        feedback_type: str,
        title: str,
        content: str,
        category: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        page_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new feedback"""
        feedback_id = f"feedback_{uuid.uuid4().hex[:12]}"
        
        feedback = FeedbackDB(
            feedback_id=feedback_id,
            user_id=user_id,
            org_id=org_id,
            feedback_type=feedback_type,
            category=category or "other",
            title=title,
            content=content,
            contact_email=contact_email,
            contact_phone=contact_phone,
            attachments=attachments or [],
            page_url=page_url,
            user_agent=user_agent,
            ip_address=ip_address,
            status="pending",
            priority="normal"
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return self._feedback_to_dict(feedback)
    
    def get_feedback(
        self,
        feedback_id: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a single feedback"""
        query = self.db.query(FeedbackDB).filter(
            FeedbackDB.feedback_id == feedback_id
        )
        
        # Users can only see their own feedback unless admin
        if user_id:
            query = query.filter(
                or_(
                    FeedbackDB.user_id == user_id,
                    FeedbackDB.user_id.is_(None)  # Allow anonymous feedback
                )
            )
        
        feedback = query.first()
        
        if not feedback:
            return None
        
        result = self._feedback_to_dict(feedback)
        
        # Include comments
        comments = self.db.query(FeedbackCommentDB).filter(
            FeedbackCommentDB.feedback_id == feedback_id
        ).order_by(FeedbackCommentDB.created_at.asc()).all()
        
        result["comments"] = [self._comment_to_dict(c) for c in comments]
        
        return result
    
    def list_feedback(
        self,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        status: Optional[str] = None,
        feedback_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List feedback with filters"""
        query = self.db.query(FeedbackDB)
        
        if user_id:
            query = query.filter(FeedbackDB.user_id == user_id)
        
        if org_id:
            query = query.filter(FeedbackDB.org_id == org_id)
        
        if status:
            query = query.filter(FeedbackDB.status == status)
        
        if feedback_type:
            query = query.filter(FeedbackDB.feedback_type == feedback_type)
        
        if category:
            query = query.filter(FeedbackDB.category == category)
        
        total = query.count()
        
        feedbacks = query.order_by(
            desc(FeedbackDB.created_at)
        ).offset(offset).limit(limit).all()
        
        return {
            "feedbacks": [self._feedback_to_dict(f) for f in feedbacks],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def update_feedback_status(
        self,
        feedback_id: str,
        status: str,
        resolution: Optional[str] = None,
        resolved_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update feedback status (admin only)"""
        feedback = self.db.query(FeedbackDB).filter(
            FeedbackDB.feedback_id == feedback_id
        ).first()
        
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")
        
        feedback.status = status
        feedback.updated_at = utc_now()
        
        if status in ["resolved", "closed"]:
            feedback.resolved_at = utc_now()
            feedback.resolved_by = resolved_by
            if resolution:
                feedback.resolution = resolution
        
        self.db.commit()
        self.db.refresh(feedback)
        
        return self._feedback_to_dict(feedback)
    
    def add_comment(
        self,
        feedback_id: str,
        user_id: Optional[str],
        content: str,
        is_admin: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a comment to feedback"""
        comment_id = f"comment_{uuid.uuid4().hex[:12]}"
        
        comment = FeedbackCommentDB(
            comment_id=comment_id,
            feedback_id=feedback_id,
            user_id=user_id,
            is_admin=is_admin,
            content=content,
            attachments=attachments or []
        )
        
        self.db.add(comment)
        
        # Update feedback updated_at
        feedback = self.db.query(FeedbackDB).filter(
            FeedbackDB.feedback_id == feedback_id
        ).first()
        if feedback:
            feedback.updated_at = utc_now()
        
        self.db.commit()
        self.db.refresh(comment)
        
        return self._comment_to_dict(comment)
    
    def submit_satisfaction_survey(
        self,
        user_id: Optional[str],
        org_id: Optional[str],
        survey_type: str,
        ratings: Dict[str, int],
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a satisfaction survey"""
        survey_id = f"survey_{uuid.uuid4().hex[:12]}"
        
        survey = SatisfactionSurveyDB(
            survey_id=survey_id,
            user_id=user_id,
            org_id=org_id,
            survey_type=survey_type,
            ratings=ratings,
            comments=comments
        )
        
        self.db.add(survey)
        self.db.commit()
        self.db.refresh(survey)
        
        return {
            "survey_id": survey_id,
            "message": "Survey submitted successfully"
        }
    
    def _feedback_to_dict(self, feedback: FeedbackDB) -> Dict[str, Any]:
        """Convert feedback to dictionary"""
        return {
            "feedback_id": feedback.feedback_id,
            "user_id": feedback.user_id,
            "org_id": feedback.org_id,
            "feedback_type": feedback.feedback_type,
            "category": feedback.category,
            "title": feedback.title,
            "content": feedback.content,
            "attachments": feedback.attachments or [],
            "contact_email": feedback.contact_email,
            "contact_phone": feedback.contact_phone,
            "status": feedback.status,
            "priority": feedback.priority,
            "assigned_to": feedback.assigned_to,
            "resolution": feedback.resolution,
            "resolved_at": feedback.resolved_at.isoformat() if feedback.resolved_at else None,
            "resolved_by": feedback.resolved_by,
            "page_url": feedback.page_url,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "updated_at": feedback.updated_at.isoformat() if feedback.updated_at else None
        }
    
    def _comment_to_dict(self, comment: FeedbackCommentDB) -> Dict[str, Any]:
        """Convert comment to dictionary"""
        return {
            "comment_id": comment.comment_id,
            "feedback_id": comment.feedback_id,
            "user_id": comment.user_id,
            "is_admin": comment.is_admin,
            "content": comment.content,
            "attachments": comment.attachments or [],
            "created_at": comment.created_at.isoformat() if comment.created_at else None
        }


def get_feedback_service(db: Session) -> FeedbackService:
    """Get feedback service instance"""
    return FeedbackService(db)
