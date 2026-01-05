"""
Pydantic models for billing-related requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================
# Plan Models
# ============================================================

class PlanResponse(BaseModel):
    """Subscription plan response."""
    id: str
    name: str
    price_cents: int
    price_formatted: str  # "R$ 29,90"
    token_limit: int
    features: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class PlansListResponse(BaseModel):
    """List of available plans."""
    success: bool
    data: List[PlanResponse]


# ============================================================
# Credit Models
# ============================================================

class CreditBalanceResponse(BaseModel):
    """Current credit balance."""
    success: bool
    data: Dict[str, Any]
    # Contains: balance, monthly_limit, used_this_period, reset_at, percentage_used


class CreditPurchase(BaseModel):
    """Credit purchase request."""
    amount: int = Field(..., ge=1000, description="Credits to purchase (min 1000)")


# ============================================================
# Usage Models
# ============================================================

class UsageRecord(BaseModel):
    """Single usage record."""
    id: str
    endpoint: str
    provider: str
    model: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_credits: int
    created_at: datetime

    class Config:
        from_attributes = True


class UsageHistoryResponse(BaseModel):
    """Usage history response."""
    success: bool
    data: List[UsageRecord]
    summary: Dict[str, Any]  # total_tokens, total_credits, by_provider, by_endpoint


class UsageSummary(BaseModel):
    """Usage summary for a period."""
    period_start: datetime
    period_end: datetime
    total_requests: int
    total_tokens: int
    total_credits: int
    by_provider: Dict[str, int]
    by_endpoint: Dict[str, int]


# ============================================================
# Transaction Models
# ============================================================

class TransactionRecord(BaseModel):
    """Single credit transaction."""
    id: str
    type: str  # 'purchase', 'subscription', 'bonus', 'usage', 'refund'
    amount: int
    balance_after: int
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionHistoryResponse(BaseModel):
    """Transaction history response."""
    success: bool
    data: List[TransactionRecord]


# ============================================================
# Subscription Models
# ============================================================

class SubscriptionCreate(BaseModel):
    """Create subscription request."""
    plan_id: str = Field(..., pattern="^(starter|pro|enterprise)$")
    payment_method_id: Optional[str] = None  # Stripe payment method


class SubscriptionResponse(BaseModel):
    """Subscription details response."""
    success: bool
    data: Dict[str, Any]
    # Contains: id, plan_id, plan_name, status, current_period_start, current_period_end, stripe_subscription_id


class SubscriptionCancel(BaseModel):
    """Cancel subscription request."""
    cancel_at_period_end: bool = True  # If True, subscription continues until period end


# ============================================================
# Stripe Models
# ============================================================

class StripeCheckoutSession(BaseModel):
    """Stripe checkout session response."""
    success: bool
    checkout_url: str
    session_id: str


class StripeBillingPortal(BaseModel):
    """Stripe billing portal response."""
    success: bool
    portal_url: str


class StripeWebhookEvent(BaseModel):
    """Stripe webhook event (for internal use)."""
    id: str
    type: str
    data: Dict[str, Any]


# ============================================================
# Response Wrapper
# ============================================================

class BillingErrorResponse(BaseModel):
    """Billing error response."""
    success: bool = False
    error: str
    code: Optional[str] = None  # Error code for frontend handling
