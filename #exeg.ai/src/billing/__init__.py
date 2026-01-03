"""
Billing module for exeg.ai.
Modelo Cline-like: pay-as-you-go + BYOK + compra avulsa de créditos.
"""
from .plans import (
    PLANS,
    CREDIT_PACKAGES,
    get_plan,
    get_package,
    get_credit_cost,
    calculate_credits,
    calculate_package_credits,
    format_price,
    format_credits,
    get_credit_price_brl,
)
from .credit_service import credit_service
from .usage_tracker import usage_tracker
from .stripe_service import stripe_service
from .pix_service import pix_service

__all__ = [
    "PLANS",
    "CREDIT_PACKAGES",
    "get_plan",
    "get_package",
    "get_credit_cost",
    "calculate_credits",
    "calculate_package_credits",
    "format_price",
    "format_credits",
    "get_credit_price_brl",
    "credit_service",
    "usage_tracker",
    "stripe_service",
    "pix_service",
]
