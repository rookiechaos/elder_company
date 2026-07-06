"""
Base Service - Base class for all services
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from services.logging_service import logger
from exceptions import ElderCompanyException, ValidationError, NotFoundError


class BaseService:
    """
    Base service class providing common functionality for all services.
    
    This class provides a unified initialization pattern and common utilities
    for all service classes in the application.
    
    Attributes:
        db: Database session instance
    """
    
    def __init__(self, db: Optional[Session] = None):
        """
        Initialize the base service.
        
        Args:
            db: Optional database session. If not provided, services should
                use dependency injection to get the session.
        """
        self.db = db
    
    def get_db(self) -> Session:
        """
        Get database session.
        
        Returns:
            Database session instance
            
        Raises:
            ValueError: If no database session is available
        """
        if self.db is None:
            raise ValueError(
                "Database session not available. "
                "Services should be initialized with a db session or use dependency injection."
            )
        return self.db
    
    def ensure_db(self) -> Session:
        """
        Ensure database session is available, raise error if not.
        
        This is a convenience method that can be used at the start of
        methods that require database access.
        
        Returns:
            Database session instance
            
        Raises:
            ValueError: If no database session is available
        """
        return self.get_db()
    
    def handle_database_error(
        self,
        error: Exception,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle database errors with proper logging and exception conversion.
        
        Args:
            error: The exception that occurred
            action: Description of the action being performed
            context: Additional context information
            
        Raises:
            ElderCompanyException: Converted exception with proper error code
        """
        logger.log_error(
            error=error,
            context={
                "action": action,
                "service": self.__class__.__name__,
                **(context or {})
            }
        )
        
        # Convert common database errors to appropriate exceptions
        error_msg = str(error).lower()
        if "not found" in error_msg or "does not exist" in error_msg:
            raise NotFoundError(f"{action} failed: Resource not found")
        elif "duplicate" in error_msg or "unique" in error_msg or "already exists" in error_msg:
            raise ValidationError(f"{action} failed: Resource already exists")
        elif "foreign key" in error_msg or "constraint" in error_msg:
            raise ValidationError(f"{action} failed: Invalid reference")
        else:
            raise ElderCompanyException(f"{action} failed: {str(error)}", "DATABASE_ERROR")
    
    def safe_commit(self, action: str = "Database operation") -> None:
        """
        Safely commit database transaction with error handling.
        
        Args:
            action: Description of the action being performed
            
        Raises:
            ElderCompanyException: If commit fails
        """
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.handle_database_error(e, action)
    
    def safe_refresh(self, obj: Any, action: str = "Refresh object") -> None:
        """
        Safely refresh database object with error handling.
        
        Args:
            obj: Object to refresh
            action: Description of the action being performed
        """
        try:
            self.db.refresh(obj)
        except Exception as e:
            logger.log_warning(
                f"Failed to refresh object: {e}",
                {"action": action, "service": self.__class__.__name__}
            )