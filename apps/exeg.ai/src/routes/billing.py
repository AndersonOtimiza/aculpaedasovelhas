"""
Billing routes for exeg.ai.
Modelo Cline-like: pay-as-you-go + BYOK + compra avulsa de créditos.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from database.init_db import get_db
from src.auth.dependencies import get_current_user, TokenData
from src.models.db_models import User, Subscription, Plan
from src.billing.credit_service import credit_service
from src.billing.usage_tracker import usage_tracker
from src.billing.stripe_service import stripe_service
from src.billing.pix_service import pix_service
from src.billing.plans import (
    PLANS,
    CREDIT_PACKAGES,
    format_price,
    format_credits,
    calculate_package_credits,
    get_credit_price_brl,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


@router.get("/credits")
async def get_credits(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current credit balance and usage stats."""
    stats = credit_service.get_usage_stats(db, token_data.user_id)
    return {
        "success": True,
        "data": stats,
    }


@router.get("/usage")
async def get_usage(
    limit: int = 50,
    offset: int = 0,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get usage history."""
    usage = usage_tracker.get_user_usage(
        db,
        token_data.user_id,
        limit=limit,
        offset=offset,
    )

    summary = usage_tracker.get_usage_summary(db, token_data.user_id)

    return {
        "success": True,
        "data": [
            {
                "id": u.id,
                "endpoint": u.endpoint,
                "provider": u.provider,
                "model": u.model,
                "input_tokens": u.input_tokens,
                "output_tokens": u.output_tokens,
                "total_tokens": u.total_tokens,
                "cost_credits": u.cost_credits,
                "created_at": u.created_at.isoformat(),
            }
            for u in usage
        ],
        "summary": summary,
    }


@router.get("/plans")
async def get_plans(db: Session = Depends(get_db)):
    """Get available subscription plans."""
    plans_list = []
    for plan_id, plan in PLANS.items():
        plans_list.append({
            "id": plan.id,
            "name": plan.name,
            "price_cents": plan.price_cents,
            "price_formatted": format_price(plan.price_cents),
            "token_limit": plan.token_limit,
            "token_limit_formatted": (
                "Ilimitado" if plan.token_limit == -1
                else f"{plan.token_limit:,}".replace(",", ".")
            ),
            "features": plan.features,
        })

    return {
        "success": True,
        "data": plans_list,
    }


@router.get("/subscription")
async def get_subscription(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current subscription details."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == token_data.user_id
    ).first()

    if not subscription:
        return {
            "success": True,
            "data": {
                "plan_id": "free",
                "plan_name": "Free",
                "status": "active",
                "current_period_end": None,
            },
        }

    plan = PLANS.get(subscription.plan_id, PLANS["free"])

    return {
        "success": True,
        "data": {
            "id": subscription.id,
            "plan_id": subscription.plan_id,
            "plan_name": plan.name,
            "status": subscription.status,
            "current_period_start": (
                subscription.current_period_start.isoformat()
                if subscription.current_period_start else None
            ),
            "current_period_end": (
                subscription.current_period_end.isoformat()
                if subscription.current_period_end else None
            ),
        },
    }


@router.post("/subscribe")
async def create_subscription(
    plan_id: str,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a subscription checkout session.

    Returns a Stripe Checkout URL to complete payment.
    """
    if not stripe_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    if plan_id not in ["starter", "pro"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan. Choose 'starter' or 'pro'",
        )

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        result = await stripe_service.create_checkout_session(
            db,
            user,
            plan_id,
            success_url="https://exeg.aculpaedasovelhas.org/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://exeg.aculpaedasovelhas.org/plans?canceled=true",
        )

        return {
            "success": True,
            "checkout_url": result["checkout_url"],
            "session_id": result["session_id"],
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/cancel")
async def cancel_subscription(
    cancel_at_period_end: bool = True,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel current subscription.

    If cancel_at_period_end is True, subscription remains active until
    the end of the current billing period.
    """
    if not stripe_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    try:
        result = await stripe_service.cancel_subscription(
            db,
            token_data.user_id,
            cancel_at_period_end=cancel_at_period_end,
        )

        return {
            "success": True,
            "message": (
                "Subscription will be canceled at period end"
                if cancel_at_period_end
                else "Subscription canceled immediately"
            ),
            "cancel_at_period_end": cancel_at_period_end,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/portal")
async def get_billing_portal(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get Stripe Billing Portal URL.

    Allows user to manage payment methods and view invoices.
    """
    if not stripe_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        result = await stripe_service.create_billing_portal_session(
            db,
            user,
            return_url="https://exeg.aculpaedasovelhas.org/billing",
        )

        return {
            "success": True,
            "portal_url": result["portal_url"],
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Stripe webhook events.

    This endpoint is called by Stripe to notify about subscription events.
    """
    if not stripe_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature",
        )

    try:
        result = await stripe_service.handle_webhook(db, payload, signature)
        return {"success": True, **result}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/packages")
async def get_credit_packages():
    """
    Get available credit packages for purchase.

    These are one-time purchases (compra avulsa) that add credits to your balance.
    Credits from packages don't expire and don't reset monthly.
    """
    packages_list = []
    for package_id, package in CREDIT_PACKAGES.items():
        total_credits = calculate_package_credits(package)
        packages_list.append({
            "id": package.id,
            "name": package.name,
            "base_credits": package.credits,
            "bonus_percent": package.bonus_percent,
            "total_credits": total_credits,
            "total_credits_formatted": format_credits(total_credits),
            "price_cents": package.price_cents,
            "price_formatted": format_price(package.price_cents),
            "price_per_1k_tokens": round(
                (package.price_cents / 100) / (total_credits / 1000), 4
            ),
        })

    return {
        "success": True,
        "data": packages_list,
        "info": {
            "currency": "BRL",
            "note": "Créditos comprados não expiram e não resetam mensalmente",
        },
    }


@router.post("/purchase-credits")
async def purchase_credits(
    package_id: str,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Purchase a credit package (compra avulsa).

    Returns a Stripe Checkout URL to complete the one-time payment.
    After payment, credits are added to your balance immediately.
    """
    if not stripe_service.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment system not configured",
        )

    package = CREDIT_PACKAGES.get(package_id)
    if not package:
        valid_packages = list(CREDIT_PACKAGES.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package. Choose one of: {valid_packages}",
        )

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        result = await stripe_service.create_credit_purchase_session(
            db,
            user,
            package,
            success_url="https://exeg.aculpaedasovelhas.org/credits/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://exeg.aculpaedasovelhas.org/credits?canceled=true",
        )

        total_credits = calculate_package_credits(package)

        return {
            "success": True,
            "checkout_url": result["checkout_url"],
            "session_id": result["session_id"],
            "package": {
                "id": package.id,
                "name": package.name,
                "credits": total_credits,
                "price_formatted": format_price(package.price_cents),
            },
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/estimate")
async def estimate_cost(
    credits: int,
):
    """
    Estimate cost in BRL for a given number of credits/tokens.

    Useful for users to understand pricing before making requests.
    """
    if credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credits must be positive",
        )

    price_brl = get_credit_price_brl(credits)

    # Find best package
    best_package = None
    best_value = float("inf")

    for package in CREDIT_PACKAGES.values():
        total_credits = calculate_package_credits(package)
        if total_credits >= credits:
            price_per_credit = package.price_cents / total_credits
            if price_per_credit < best_value:
                best_value = price_per_credit
                best_package = package

    recommendation = None
    if best_package:
        recommendation = {
            "package_id": best_package.id,
            "package_name": best_package.name,
            "total_credits": calculate_package_credits(best_package),
            "price_formatted": format_price(best_package.price_cents),
        }

    return {
        "success": True,
        "data": {
            "credits": credits,
            "credits_formatted": format_credits(credits),
            "estimated_price_brl": round(price_brl, 2),
            "estimated_price_formatted": f"R$ {price_brl:.2f}".replace(".", ","),
            "recommended_package": recommendation,
        },
    }


# =============================================================================
# PIX - Otimiza Pagamentos (Modelo Binance)
# =============================================================================

@router.post("/pix/create")
async def create_pix_order(
    package_id: str,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a PIX payment order (Otimiza Pagamentos).

    Modelo Binance:
    1. Gera QR Code e código PIX
    2. Usuário faz o pagamento
    3. Envia comprovante via WhatsApp para a ANA
    4. ANA valida e carrega os créditos automaticamente

    Returns PIX code, QR code, and WhatsApp instructions.
    """
    package = CREDIT_PACKAGES.get(package_id)
    if not package:
        valid_packages = list(CREDIT_PACKAGES.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid package. Choose one of: {valid_packages}",
        )

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        result = await pix_service.create_pix_order(db, user, package_id)
        return {"success": True, **result}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/pix/status/{transaction_id}")
async def get_pix_status(
    transaction_id: str,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get status of a PIX transaction.

    Status values:
    - pending: Order created, awaiting payment
    - awaiting_receipt: Payment made, waiting for receipt via WhatsApp
    - validating: ANA is validating the receipt
    - confirmed: Payment confirmed, credits added
    - rejected: Payment rejected (invalid receipt)
    - expired: Order expired (24h timeout)
    """
    result = await pix_service.get_transaction_status(
        db, token_data.user_id, transaction_id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return {"success": True, "data": result}


@router.get("/pix/history")
async def get_pix_history(
    limit: int = 20,
    offset: int = 0,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's PIX transaction history."""
    transactions = await pix_service.list_user_transactions(
        db, token_data.user_id, limit, offset
    )

    return {
        "success": True,
        "data": transactions,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "count": len(transactions),
        },
    }


@router.post("/pix/webhook/otimiza")
async def otimiza_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Webhook for Otimiza Pagamentos (ANA).

    Called by ANA after validating a PIX receipt.
    Requires signature verification for security.

    Expected payload:
    {
        "event": "payment.confirmed" | "payment.rejected",
        "transaction_id": "uuid",
        "bank_transaction_id": "...",
        "validated_by": "ana_ai",
        "notes": "Optional validation notes",
        "reason": "Rejection reason (if rejected)"
    }
    """
    payload = await request.body()
    signature = request.headers.get("X-Otimiza-Signature")

    # Verify signature
    if signature and not pix_service.verify_webhook_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    try:
        import json
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    event = data.get("event")
    transaction_id = data.get("transaction_id")

    if not event or not transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields: event, transaction_id",
        )

    try:
        if event == "payment.confirmed":
            result = await pix_service.confirm_payment(
                db,
                transaction_id,
                bank_transaction_id=data.get("bank_transaction_id", ""),
                validated_by=data.get("validated_by", "ana_ai"),
                notes=data.get("notes"),
            )
        elif event == "payment.rejected":
            result = await pix_service.reject_payment(
                db,
                transaction_id,
                reason=data.get("reason", "Receipt validation failed"),
                validated_by=data.get("validated_by", "ana_ai"),
            )
        else:
            return {"success": False, "error": f"Unknown event: {event}"}

        return {"success": True, **result}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/pix/info")
async def get_pix_info():
    """
    Get PIX payment information.

    Returns Otimiza Pagamentos details and instructions.
    """
    return {
        "success": True,
        "data": {
            "provider": "Otimiza Pagamentos",
            "pix_key": pix_service.PIX_KEY,
            "pix_key_type": pix_service.PIX_KEY_TYPE,
            "beneficiary": pix_service.BENEFICIARY_NAME,
            "whatsapp": {
                "number": pix_service._whatsapp_number,
                "name": "ANA (IA Otimiza)",
                "purpose": "Enviar comprovante de pagamento para validação",
            },
            "instructions": [
                "1. Escolha um pacote de créditos",
                "2. Gere o QR Code PIX",
                "3. Faça o pagamento no seu banco",
                "4. Envie o comprovante pelo WhatsApp da Otimiza",
                "5. A ANA (IA) validará automaticamente",
                "6. Créditos serão adicionados em até 5 minutos",
            ],
            "packages": [
                {
                    "id": pkg.id,
                    "name": pkg.name,
                    "price_formatted": format_price(pkg.price_cents),
                    "credits": calculate_package_credits(pkg),
                    "credits_formatted": format_credits(calculate_package_credits(pkg)),
                    "bonus_percent": pkg.bonus_percent,
                }
                for pkg in CREDIT_PACKAGES.values()
            ],
        },
    }
