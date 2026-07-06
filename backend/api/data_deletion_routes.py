"""
Data Deletion Routes - Account deletion (GDPR compliant)
Data Deletion Routes - Account deletion (GDPR compliant)
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from dependencies import require_auth, get_data_deletion_service_dependency
from services.data_deletion_service import DataDeletionService
from middleware.api_decorators import handle_api_errors
from exceptions import AuthenticationError, ValidationError

router = APIRouter(prefix="/api/account", tags=["account"])


class DeleteAccountRequest(BaseModel):
    """Delete account request"""
    confirmation: str = "DELETE"  # Confirmation text
    reason: Optional[str] = None  # Optional reason for deletion


@router.get("/deletion-summary")
@handle_api_errors
async def get_deletion_summary(
    current_user: dict = Depends(require_auth),
    deletion_service: DataDeletionService = Depends(get_data_deletion_service_dependency)
):
    """Get account deletion summary (what data will be removed)"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise AuthenticationError("User not authenticated")
    
    summary = deletion_service.get_deletion_summary(user_id)
    
    return summary


@router.post("/delete")
@handle_api_errors
async def delete_account(
    request: DeleteAccountRequest,
    current_user: dict = Depends(require_auth),
    deletion_service: DataDeletionService = Depends(get_data_deletion_service_dependency)
):
    """
    Delete account and all associated data (GDPR compliant)
    
    Warning: this operation is irreversible!
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise AuthenticationError("User not authenticated")
    
    # Require confirmation
    if request.confirmation != "DELETE":
        raise ValidationError("Confirmation required. Please type 'DELETE' to confirm.")
    
    # Perform deletion
    result = deletion_service.delete_user_account(user_id)
    
    return {
        "message": "Account and all associated data have been deleted successfully",
        "deletion_summary": result,
        "note": "This action is irreversible. All your data has been permanently deleted."
    }


@router.post("/request-deletion")
@handle_api_errors
async def request_account_deletion(
    current_user: dict = Depends(require_auth),
    deletion_service: DataDeletionService = Depends(get_data_deletion_service_dependency)
):
    """Request account deletion (create deletion request)"""
    user_id = current_user.get("user_id")
    if not user_id:
        raise AuthenticationError("User not authenticated")
    
    result = deletion_service.request_account_deletion(user_id)
    
    return result
