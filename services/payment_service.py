"""
Payment Service - Payment and subscription management
"""

import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from utils.time_utils import utc_now
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from models.payment_models import PaymentDB, SubscriptionDB, InvoiceDB
from models.database import OrganizationDB


class PaymentService:
    """Service for payment and subscription management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stripe_enabled = os.getenv("STRIPE_SECRET_KEY") is not None
    
    def create_subscription(
        self,
        org_id: str,
        plan_id: str,
        user_id: Optional[str] = None,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a subscription"""
        # Get plan details
        plan_details = self._get_plan_details(plan_id)
        
        subscription_id = f"sub_{uuid.uuid4().hex[:12]}"
        
        # Calculate period
        now = utc_now()
        if plan_details.get("billing_cycle") == "yearly":
            period_end = now + timedelta(days=365)
        else:
            period_end = now + timedelta(days=30)
        
        subscription = SubscriptionDB(
            subscription_id=subscription_id,
            org_id=org_id,
            user_id=user_id,
            plan_id=plan_id,
            plan_name=plan_details.get("name", plan_id),
            amount=plan_details.get("amount", 0),
            currency=plan_details.get("currency", "JPY"),
            billing_cycle=plan_details.get("billing_cycle", "monthly"),
            status="active",
            current_period_start=now,
            current_period_end=period_end,
            auto_renew=True
        )
        
        self.db.add(subscription)
        
        # Update organization subscription
        org = self.db.query(OrganizationDB).filter(
            OrganizationDB.org_id == org_id
        ).first()
        if org:
            org.subscription_plan = plan_id
            org.monthly_translation_limit = plan_details.get("translation_limit", 0)
            org.max_users = plan_details.get("max_users", 0)
        
        # TODO: Integrate with Stripe if enabled
        if self.stripe_enabled and payment_method_id:
            try:
                import stripe
                stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
                
                # Create Stripe subscription
                # Note: In production, stripe_customer_id should be stored in OrganizationDB
                # For now, create subscription without customer (will need customer setup)
                if plan_details.get("stripe_price_id"):
                    stripe_subscription = stripe.Subscription.create(
                        items=[{"price": plan_details.get("stripe_price_id")}],
                        payment_behavior="default_incomplete",
                        payment_settings={"save_default_payment_method": "on_subscription"},
                        expand=["latest_invoice.payment_intent"]
                    )
                    subscription.provider_subscription_id = stripe_subscription.id
            except Exception as e:
                print(f"Stripe integration error: {e}")
                # Continue without Stripe integration
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return self._subscription_to_dict(subscription)
    
    def cancel_subscription(
        self,
        subscription_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        subscription = self.db.query(SubscriptionDB).filter(
            SubscriptionDB.subscription_id == subscription_id
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        subscription.status = "canceled"
        subscription.canceled_at = utc_now()
        subscription.canceled_by = user_id
        subscription.auto_renew = False
        
        # TODO: Cancel Stripe subscription if enabled
        if self.stripe_enabled and subscription.provider_subscription_id:
            try:
                import stripe
                stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
                stripe.Subscription.modify(
                    subscription.provider_subscription_id,
                    cancel_at_period_end=True
                )
            except Exception as e:
                print(f"Stripe cancellation error: {e}")
        
        self.db.commit()
        self.db.refresh(subscription)
        
        return self._subscription_to_dict(subscription)
    
    def get_subscription(
        self,
        org_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get organization subscription"""
        subscription = self.db.query(SubscriptionDB).filter(
            and_(
                SubscriptionDB.org_id == org_id,
                SubscriptionDB.status == "active"
            )
        ).order_by(desc(SubscriptionDB.created_at)).first()
        
        if not subscription:
            return None
        
        return self._subscription_to_dict(subscription)
    
    def create_invoice(
        self,
        org_id: str,
        subscription_id: Optional[str],
        amount: float,
        items: List[Dict[str, Any]],
        currency: str = "JPY"
    ) -> Dict[str, Any]:
        """Create an invoice"""
        invoice_id = f"inv_{uuid.uuid4().hex[:12]}"
        invoice_number = f"INV-{utc_now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        invoice = InvoiceDB(
            invoice_id=invoice_id,
            org_id=org_id,
            subscription_id=subscription_id,
            invoice_number=invoice_number,
            amount=amount,
            currency=currency,
            items=items,
            status="draft",
            issue_date=utc_now(),
            due_date=utc_now() + timedelta(days=30)
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        
        return self._invoice_to_dict(invoice)
    
    def get_payment_history(
        self,
        org_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get payment history"""
        payments = self.db.query(PaymentDB).filter(
            PaymentDB.org_id == org_id
        ).order_by(desc(PaymentDB.created_at)).offset(offset).limit(limit).all()
        
        total = self.db.query(PaymentDB).filter(
            PaymentDB.org_id == org_id
        ).count()
        
        return {
            "payments": [self._payment_to_dict(p) for p in payments],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def _get_plan_details(self, plan_id: str) -> Dict[str, Any]:
        """Get plan details"""
        plans = {
            "basic": {
                "name": "Basic Plan",
                "amount": 5000,  # JPY per month
                "currency": "JPY",
                "billing_cycle": "monthly",
                "max_users": 10,
                "translation_limit": 1000
            },
            "professional": {
                "name": "Professional Plan",
                "amount": 15000,
                "currency": "JPY",
                "billing_cycle": "monthly",
                "max_users": 50,
                "translation_limit": 10000
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "amount": 50000,
                "currency": "JPY",
                "billing_cycle": "monthly",
                "max_users": -1,  # Unlimited
                "translation_limit": -1  # Unlimited
            }
        }
        
        return plans.get(plan_id, plans["basic"])
    
    def _subscription_to_dict(self, subscription: SubscriptionDB) -> Dict[str, Any]:
        """Convert subscription to dictionary"""
        return {
            "subscription_id": subscription.subscription_id,
            "org_id": subscription.org_id,
            "plan_id": subscription.plan_id,
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "amount": subscription.amount,
            "currency": subscription.currency,
            "billing_cycle": subscription.billing_cycle,
            "current_period_start": subscription.current_period_start.isoformat(),
            "current_period_end": subscription.current_period_end.isoformat(),
            "auto_renew": subscription.auto_renew,
            "canceled_at": subscription.canceled_at.isoformat() if subscription.canceled_at else None,
            "created_at": subscription.created_at.isoformat()
        }
    
    def _payment_to_dict(self, payment: PaymentDB) -> Dict[str, Any]:
        """Convert payment to dictionary"""
        return {
            "payment_id": payment.payment_id,
            "org_id": payment.org_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "subscription_id": payment.subscription_id,
            "created_at": payment.created_at.isoformat(),
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
        }
    
    def _invoice_to_dict(self, invoice: InvoiceDB) -> Dict[str, Any]:
        """Convert invoice to dictionary"""
        return {
            "invoice_id": invoice.invoice_id,
            "invoice_number": invoice.invoice_number,
            "org_id": invoice.org_id,
            "amount": invoice.amount,
            "currency": invoice.currency,
            "status": invoice.status,
            "items": invoice.items,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "pdf_url": invoice.pdf_url
        }


def get_payment_service(db: Session) -> PaymentService:
    """Get payment service instance"""
    return PaymentService(db)
