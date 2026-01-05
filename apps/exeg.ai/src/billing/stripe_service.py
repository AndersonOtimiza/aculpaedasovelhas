"""
Stripe integration service for exeg.ai.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import stripe

from src.config.settings import settings
from src.models.db_models import User, Subscription, Credit
from .plans import PLANS, CreditPackage, calculate_package_credits
from .credit_service import credit_service


class StripeService:
    """Service for Stripe payment integration."""

    def __init__(self):
        """Initialize Stripe with API key."""
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        self._initialized = bool(settings.STRIPE_SECRET_KEY)

    @property
    def is_configured(self) -> bool:
        """Check if Stripe is configured."""
        return self._initialized

    def _require_stripe(self) -> None:
        """Raise error if Stripe is not configured."""
        if not self._initialized:
            raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY in .env")

    async def create_customer(
        self,
        db: Session,
        user: User,
    ) -> Optional[str]:
        """
        Create a Stripe customer for a user.

        Args:
            db: Database session
            user: User object

        Returns:
            Stripe customer ID
        """
        self._require_stripe()

        # Check if user already has a Stripe customer ID
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

        if subscription and subscription.stripe_customer_id:
            return subscription.stripe_customer_id

        # Create Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": user.id},
        )

        # Update subscription with customer ID
        if subscription:
            subscription.stripe_customer_id = customer.id
            db.commit()

        return customer.id

    async def create_checkout_session(
        self,
        db: Session,
        user: User,
        plan_id: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            db: Database session
            user: User object
            plan_id: Plan ID ('starter' or 'pro')
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            Dict with checkout URL and session ID
        """
        self._require_stripe()

        if plan_id not in ["starter", "pro"]:
            raise ValueError(f"Invalid plan: {plan_id}")

        # Get price ID from settings
        price_id = (
            settings.STRIPE_PRICE_STARTER
            if plan_id == "starter"
            else settings.STRIPE_PRICE_PRO
        )

        if not price_id:
            raise ValueError(f"Stripe price not configured for plan: {plan_id}")

        # Get or create customer
        customer_id = await self.create_customer(db, user)

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "plan_id": plan_id,
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    async def create_credit_purchase_session(
        self,
        db: Session,
        user: User,
        package: CreditPackage,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for one-time credit purchase.

        Args:
            db: Database session
            user: User object
            package: CreditPackage to purchase
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            Dict with checkout URL and session ID
        """
        self._require_stripe()

        # Get or create customer
        customer_id = await self.create_customer(db, user)

        total_credits = calculate_package_credits(package)

        # Create checkout session for one-time payment
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card", "boleto", "pix"],
            line_items=[
                {
                    "price_data": {
                        "currency": "brl",
                        "product_data": {
                            "name": f"{package.name} - {total_credits:,} créditos".replace(",", "."),
                            "description": f"Pacote de créditos para exeg.ai ({package.bonus_percent}% bônus)" if package.bonus_percent else "Pacote de créditos para exeg.ai",
                        },
                        "unit_amount": package.price_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "package_id": package.id,
                "credits": str(total_credits),
                "type": "credit_purchase",
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    async def create_billing_portal_session(
        self,
        db: Session,
        user: User,
        return_url: str,
    ) -> Dict[str, Any]:
        """
        Create a Stripe Billing Portal session.

        Args:
            db: Database session
            user: User object
            return_url: URL to return after portal

        Returns:
            Dict with portal URL
        """
        self._require_stripe()

        # Get subscription to find customer ID
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id
        ).first()

        if not subscription or not subscription.stripe_customer_id:
            raise ValueError("User does not have a Stripe subscription")

        # Create portal session
        session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=return_url,
        )

        return {
            "portal_url": session.url,
        }

    async def handle_webhook(
        self,
        db: Session,
        payload: bytes,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.

        Args:
            db: Database session
            payload: Raw webhook payload
            signature: Stripe signature header

        Returns:
            Dict with event handling result
        """
        self._require_stripe()

        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid webhook signature")

        event_type = event["type"]
        data = event["data"]["object"]

        # Handle different event types
        if event_type == "checkout.session.completed":
            return await self._handle_checkout_completed(db, data)
        elif event_type == "customer.subscription.updated":
            return await self._handle_subscription_updated(db, data)
        elif event_type == "customer.subscription.deleted":
            return await self._handle_subscription_deleted(db, data)
        elif event_type == "invoice.paid":
            return await self._handle_invoice_paid(db, data)
        elif event_type == "invoice.payment_failed":
            return await self._handle_payment_failed(db, data)

        return {"handled": False, "event_type": event_type}

    async def _handle_checkout_completed(
        self,
        db: Session,
        data: Dict,
    ) -> Dict[str, Any]:
        """Handle successful checkout."""
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        checkout_type = metadata.get("type")

        if not user_id:
            return {"handled": False, "error": "Missing user_id in metadata"}

        # Handle credit purchase
        if checkout_type == "credit_purchase":
            return await self._handle_credit_purchase(db, data, metadata)

        # Handle subscription
        plan_id = metadata.get("plan_id")
        if not plan_id:
            return {"handled": False, "error": "Missing plan_id in metadata"}

        # Get user's subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()

        if subscription:
            # Update subscription
            subscription.plan_id = plan_id
            subscription.stripe_subscription_id = data.get("subscription")
            subscription.stripe_customer_id = data.get("customer")
            subscription.status = "active"
        else:
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                stripe_subscription_id=data.get("subscription"),
                stripe_customer_id=data.get("customer"),
                status="active",
            )
            db.add(subscription)

        # Update credits
        plan = PLANS.get(plan_id)
        if plan:
            credit_service.add_credits(
                db,
                user_id,
                plan.token_limit,
                transaction_type="subscription",
                description=f"Upgrade to {plan.name} plan",
            )

            # Update credit limits
            credit = db.query(Credit).filter(Credit.user_id == user_id).first()
            if credit:
                credit.monthly_limit = plan.token_limit

        db.commit()
        return {"handled": True, "action": "subscription_created"}

    async def _handle_credit_purchase(
        self,
        db: Session,
        data: Dict,
        metadata: Dict,
    ) -> Dict[str, Any]:
        """Handle successful credit package purchase."""
        user_id = metadata.get("user_id")
        package_id = metadata.get("package_id")
        credits = int(metadata.get("credits", 0))

        if not credits:
            return {"handled": False, "error": "Missing credits in metadata"}

        # Add credits to user's balance
        credit_service.add_credits(
            db,
            user_id,
            credits,
            transaction_type="purchase",
            description=f"Compra de pacote {package_id}: {credits:,} créditos".replace(",", "."),
            stripe_payment_id=data.get("payment_intent"),
        )

        db.commit()
        return {
            "handled": True,
            "action": "credits_purchased",
            "credits": credits,
            "package_id": package_id,
        }

    async def _handle_subscription_updated(
        self,
        db: Session,
        data: Dict,
    ) -> Dict[str, Any]:
        """Handle subscription updates."""
        stripe_sub_id = data.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

        if not subscription:
            return {"handled": False, "error": "Subscription not found"}

        # Update status
        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "canceled",
            "unpaid": "past_due",
            "trialing": "trialing",
        }
        subscription.status = status_map.get(data.get("status"), "active")

        db.commit()
        return {"handled": True, "action": "subscription_updated"}

    async def _handle_subscription_deleted(
        self,
        db: Session,
        data: Dict,
    ) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        stripe_sub_id = data.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()

        if not subscription:
            return {"handled": False, "error": "Subscription not found"}

        # Downgrade to free plan
        subscription.plan_id = "free"
        subscription.status = "canceled"
        subscription.stripe_subscription_id = None

        # Update credit limits
        credit = db.query(Credit).filter(
            Credit.user_id == subscription.user_id
        ).first()
        if credit:
            credit.monthly_limit = PLANS["free"].token_limit

        db.commit()
        return {"handled": True, "action": "subscription_canceled"}

    async def _handle_invoice_paid(
        self,
        db: Session,
        data: Dict,
    ) -> Dict[str, Any]:
        """Handle successful invoice payment (subscription renewal)."""
        customer_id = data.get("customer")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if not subscription:
            return {"handled": False, "error": "Subscription not found"}

        # Add monthly credits
        plan = PLANS.get(subscription.plan_id)
        if plan:
            credit_service.reset_monthly_credits(db, subscription.user_id)

        return {"handled": True, "action": "credits_renewed"}

    async def _handle_payment_failed(
        self,
        db: Session,
        data: Dict,
    ) -> Dict[str, Any]:
        """Handle failed payment."""
        customer_id = data.get("customer")

        subscription = db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()

        if subscription:
            subscription.status = "past_due"
            db.commit()

        return {"handled": True, "action": "marked_past_due"}

    async def cancel_subscription(
        self,
        db: Session,
        user_id: str,
        cancel_at_period_end: bool = True,
    ) -> Dict[str, Any]:
        """
        Cancel a user's subscription.

        Args:
            db: Database session
            user_id: User ID
            cancel_at_period_end: If True, subscription continues until period end

        Returns:
            Dict with cancellation result
        """
        self._require_stripe()

        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()

        if not subscription or not subscription.stripe_subscription_id:
            raise ValueError("No active subscription found")

        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=cancel_at_period_end,
        )

        if not cancel_at_period_end:
            subscription.status = "canceled"
            subscription.plan_id = "free"
            db.commit()

        return {
            "success": True,
            "cancel_at_period_end": cancel_at_period_end,
        }


# Singleton instance
stripe_service = StripeService()
