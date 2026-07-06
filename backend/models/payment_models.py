"""
Payment Models - Payment and subscription management
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Float
from datetime import datetime
from models.database import Base


class PaymentDB(Base):
    """Payment record table"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    user_id = Column(String, index=True, nullable=True)
    org_id = Column(String, index=True, nullable=False)
    
    # Payment fields
    amount = Column(Float, nullable=False)  # Amount
    currency = Column(String, default="JPY")  # Currency
    payment_method = Column(String, nullable=False)  # stripe, paypal, etc.
    payment_provider_id = Column(String, nullable=True)  # Provider payment ID
    
    # Payment status
    status = Column(String, default="pending", index=True)  # pending, processing, completed, failed, refunded
    payment_intent_id = Column(String, nullable=True)  # Stripe payment intent ID
    
    # Subscription fields
    subscription_id = Column(String, index=True, nullable=True)  # Linked subscription
    plan_id = Column(String, nullable=True)  # Subscription plan ID
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)  # Other metadata (metadata is SQLAlchemy reserved)
    receipt_url = Column(String, nullable=True)  # Receipt URL
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubscriptionDB(Base):
    """Subscription table"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # Subscription creator
    
    # Subscription fields
    plan_id = Column(String, nullable=False)  # basic, professional, enterprise
    plan_name = Column(String, nullable=False)
    
    # Subscription status
    status = Column(String, default="active", index=True)  # active, canceled, expired, past_due
    provider_subscription_id = Column(String, nullable=True)  # Stripe subscription ID
    
    # Billing fields
    amount = Column(Float, nullable=False)  # Monthly fee
    currency = Column(String, default="JPY")
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    
    # Timestamps
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    canceled_by = Column(String, nullable=True)
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True)
    
    # Metadata
    extra_metadata = Column(JSON, nullable=True)  # Other metadata (metadata is SQLAlchemy reserved)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvoiceDB(Base):
    """Invoice table"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, unique=True, index=True, nullable=False)
    
    # Relationship / linkage fields
    org_id = Column(String, index=True, nullable=False)
    subscription_id = Column(String, index=True, nullable=True)
    payment_id = Column(String, index=True, nullable=True)
    
    # Invoice fields
    invoice_number = Column(String, unique=True, nullable=False)  # Invoice number
    amount = Column(Float, nullable=False)
    currency = Column(String, default="JPY")
    tax_amount = Column(Float, default=0.0)
    
    # Invoice status
    status = Column(String, default="draft", index=True)  # draft, sent, paid, overdue, void
    
    # Invoice content
    items = Column(JSON, nullable=False)  # Invoice line items
    billing_address = Column(JSON, nullable=True)  # Billing address
    
    # Timestamps
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # PDF URL
    pdf_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
