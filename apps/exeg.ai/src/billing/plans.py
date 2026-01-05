"""
Subscription plans and credit costs for exeg.ai.
Modelo inspirado no Cline.bot: pay-as-you-go + BYOK em todos os planos.
"""
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class PlanConfig:
    """Plan configuration."""
    id: str
    name: str
    price_cents: int  # Price in cents (R$ 29.90 = 2990)
    token_limit: int  # Monthly token limit (-1 for unlimited, 0 for pay-as-you-go)
    features: Dict


@dataclass
class CreditPackage:
    """Credit package for purchase."""
    id: str
    name: str
    credits: int
    price_cents: int
    bonus_percent: int  # Bonus percentage (e.g., 10 = 10% extra)


# Plan definitions (modelo híbrido: assinatura + pay-as-you-go)
PLANS: Dict[str, PlanConfig] = {
    "free": PlanConfig(
        id="free",
        name="Free",
        price_cents=0,
        token_limit=10000,  # 10k tokens/month
        features={
            "providers": ["ollama", "openai", "anthropic"],
            "support": "community",
            "api_access": True,
            "byok": True,  # BYOK habilitado para todos
            "can_purchase_credits": True,
        },
    ),
    "pay_as_you_go": PlanConfig(
        id="pay_as_you_go",
        name="Pay-as-you-go",
        price_cents=0,
        token_limit=0,  # Sem limite mensal, paga por uso
        features={
            "providers": ["ollama", "openai", "anthropic"],
            "support": "community",
            "api_access": True,
            "byok": True,
            "can_purchase_credits": True,
            "no_monthly_reset": True,  # Créditos não expiram
        },
    ),
    "starter": PlanConfig(
        id="starter",
        name="Starter",
        price_cents=2990,  # R$ 29.90
        token_limit=100000,  # 100k tokens/month
        features={
            "providers": ["ollama", "openai", "anthropic"],
            "support": "email",
            "api_access": True,
            "priority": False,
            "byok": True,
            "can_purchase_credits": True,
        },
    ),
    "pro": PlanConfig(
        id="pro",
        name="Pro",
        price_cents=9990,  # R$ 99.90
        token_limit=500000,  # 500k tokens/month
        features={
            "providers": ["ollama", "openai", "anthropic"],
            "support": "priority",
            "api_access": True,
            "priority": True,
            "byok": True,
            "can_purchase_credits": True,
        },
    ),
    "enterprise": PlanConfig(
        id="enterprise",
        name="Enterprise",
        price_cents=0,  # Custom pricing
        token_limit=-1,  # Unlimited
        features={
            "providers": ["ollama", "openai", "anthropic"],
            "support": "dedicated",
            "api_access": True,
            "priority": True,
            "byok": True,
            "custom_models": True,
            "can_purchase_credits": False,  # Já é ilimitado
        },
    ),
}


# Credit packages for purchase (compra avulsa)
CREDIT_PACKAGES: Dict[str, CreditPackage] = {
    "small": CreditPackage(
        id="small",
        name="Pacote Pequeno",
        credits=50000,  # 50k tokens
        price_cents=990,  # R$ 9.90
        bonus_percent=0,
    ),
    "medium": CreditPackage(
        id="medium",
        name="Pacote Médio",
        credits=200000,  # 200k tokens
        price_cents=2990,  # R$ 29.90
        bonus_percent=10,  # +10% = 220k tokens
    ),
    "large": CreditPackage(
        id="large",
        name="Pacote Grande",
        credits=500000,  # 500k tokens
        price_cents=5990,  # R$ 59.90
        bonus_percent=20,  # +20% = 600k tokens
    ),
    "mega": CreditPackage(
        id="mega",
        name="Pacote Mega",
        credits=1000000,  # 1M tokens
        price_cents=9990,  # R$ 99.90
        bonus_percent=30,  # +30% = 1.3M tokens
    ),
}


# Credit costs per provider/model (credits per 1000 tokens)
CREDIT_COSTS: Dict[str, Dict[str, int]] = {
    "ollama": {
        "default": 1,  # 1 credit per 1000 tokens (local, free)
        "qwen3:4b": 1,
        "llama3:8b": 1,
        "mistral": 1,
    },
    "openai": {
        "default": 5,  # 5 credits per 1000 tokens
        "gpt-4o-mini": 5,
        "gpt-4o": 25,
        "gpt-4": 50,
    },
    "anthropic": {
        "default": 5,  # 5 credits per 1000 tokens
        "claude-3-haiku-20240307": 5,
        "claude-3-sonnet-20240229": 30,
        "claude-3-opus-20240229": 75,
    },
}


def get_plan(plan_id: str) -> Optional[PlanConfig]:
    """Get plan configuration by ID."""
    return PLANS.get(plan_id)


def get_credit_cost(provider: str, model: Optional[str] = None) -> int:
    """
    Get credit cost per 1000 tokens for a provider/model.

    Args:
        provider: LLM provider ('ollama', 'openai', 'anthropic')
        model: Optional model name

    Returns:
        Credits per 1000 tokens
    """
    provider_costs = CREDIT_COSTS.get(provider, {"default": 1})

    if model and model in provider_costs:
        return provider_costs[model]

    return provider_costs.get("default", 1)


def calculate_credits(provider: str, model: Optional[str], total_tokens: int) -> int:
    """
    Calculate credits needed for a given number of tokens.

    Args:
        provider: LLM provider
        model: Model name
        total_tokens: Total tokens used

    Returns:
        Credits to deduct
    """
    cost_per_1k = get_credit_cost(provider, model)
    # Round up to ensure we always charge at least the minimum
    return max(1, (total_tokens * cost_per_1k + 999) // 1000)


def format_price(price_cents: int) -> str:
    """Format price in cents to BRL string."""
    if price_cents == 0:
        return "Grátis"
    return f"R$ {price_cents / 100:.2f}".replace(".", ",")


def get_package(package_id: str) -> Optional[CreditPackage]:
    """Get credit package by ID."""
    return CREDIT_PACKAGES.get(package_id)


def calculate_package_credits(package: CreditPackage) -> int:
    """Calculate total credits including bonus."""
    bonus = (package.credits * package.bonus_percent) // 100
    return package.credits + bonus


def get_credit_price_brl(credits: int) -> float:
    """
    Calculate approximate BRL price for credits.
    Based on the medium package: R$ 29.90 for 200k tokens (with 10% bonus = 220k).
    Base rate: ~R$ 0.136 per 1000 tokens.
    """
    # Base rate: R$ 29.90 / 220.000 = R$ 0.000136 per token
    # Or: R$ 0.136 per 1000 tokens
    rate_per_1k = 0.136
    return (credits / 1000) * rate_per_1k


def format_credits(credits: int) -> str:
    """Format credits to human-readable string."""
    if credits >= 1000000:
        return f"{credits / 1000000:.1f}M".replace(".", ",")
    elif credits >= 1000:
        return f"{credits / 1000:.0f}k"
    return str(credits)
