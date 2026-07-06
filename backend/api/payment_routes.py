"""
Payment Routes - Payment and subscription management
Payment Routes - Payment and subscription management
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from dependencies import require_auth, get_payment_service_dependency
from services.payment_service import PaymentService
from middleware.api_decorators import handle_api_errors
from exceptions import ValidationError, NotFoundError

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CreateSubscriptionRequest(BaseModel):
    """Create subscription request"""
    plan_id: str  # basic, professional, enterprise
    payment_method_id: Optional[str] = None  # Stripe payment method ID


class CancelSubscriptionRequest(BaseModel):
    """Cancel subscription request"""
    reason: Optional[str] = None


@router.post("/subscriptions")
@handle_api_errors
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: dict = Depends(require_auth),
    payment_service: PaymentService = Depends(get_payment_service_dependency)
):
    """Create subscription"""
    org_id = current_user.get("org_id")
    if not org_id:
        raise ValidationError("Organization ID required")
    
    subscription = payment_service.create_subscription(
        org_id=org_id,
        plan_id=request.plan_id,
        user_id=current_user.get("user_id"),
        payment_method_id=request.payment_method_id
    )
    
    return subscription


@router.get("/subscriptions")
@handle_api_errors
async def get_subscription(
    current_user: dict = Depends(require_auth),
    payment_service: PaymentService = Depends(get_payment_service_dependency)
):
    """Get current subscription"""
    org_id = current_user.get("org_id")
    if not org_id:
        raise ValidationError("Organization ID required")
    
    subscription = payment_service.get_subscription(org_id)
    
    if not subscription:
        return {"message": "No active subscription found"}
    
    return subscription


@router.post("/subscriptions/{subscription_id}/cancel")
@handle_api_errors
async def cancel_subscription(
    subscription_id: str,
    request: CancelSubscriptionRequest,
    current_user: dict = Depends(require_auth),
    payment_service: PaymentService = Depends(get_payment_service_dependency)
):
    """Cancel subscription"""
    subscription = payment_service.cancel_subscription(
        subscription_id=subscription_id,
        user_id=current_user.get("user_id")
    )
    
    return subscription


@router.get("/history")
@handle_api_errors
async def get_payment_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_auth),
    payment_service: PaymentService = Depends(get_payment_service_dependency)
):
    """Get payment history"""
    org_id = current_user.get("org_id")
    if not org_id:
        raise ValidationError("Organization ID required")
    
    result = payment_service.get_payment_history(
        org_id=org_id,
        limit=limit,
        offset=offset
    )
    
    return result
