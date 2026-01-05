"""
Credit management service for exeg.ai.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from src.models.db_models import Credit, CreditTransaction, User, Subscription
from .plans import PLANS, calculate_credits


class CreditService:
    """Service for managing user credits."""

    def get_user_credits(self, db: Session, user_id: str) -> Optional[Credit]:
        """Get user's credit record."""
        return db.query(Credit).filter(Credit.user_id == user_id).first()

    def get_balance(self, db: Session, user_id: str) -> int:
        """Get user's current credit balance."""
        credit = self.get_user_credits(db, user_id)
        return credit.balance if credit else 0

    def check_sufficient_credits(
        self, db: Session, user_id: str, required: int
    ) -> Tuple[bool, int]:
        """
        Check if user has sufficient credits.

        Returns:
            Tuple of (has_sufficient, current_balance)
        """
        credit = self.get_user_credits(db, user_id)
        if not credit:
            return False, 0

        # Check if reset is needed
        self._check_and_reset_monthly(db, credit)

        return credit.balance >= required, credit.balance

    def deduct_credits(
        self,
        db: Session,
        user_id: str,
        amount: int,
        description: str = "Usage",
    ) -> Tuple[bool, int]:
        """
        Deduct credits from user's balance.

        Args:
            db: Database session
            user_id: User ID
            amount: Credits to deduct
            description: Transaction description

        Returns:
            Tuple of (success, new_balance)
        """
        credit = self.get_user_credits(db, user_id)
        if not credit:
            return False, 0

        # Check if reset is needed
        self._check_and_reset_monthly(db, credit)

        if credit.balance < amount:
            return False, credit.balance

        # Deduct credits
        credit.balance -= amount
        credit.used_this_period += amount
        new_balance = credit.balance

        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            type="usage",
            amount=-amount,
            balance_after=new_balance,
            description=description,
        )
        db.add(transaction)

        db.commit()
        return True, new_balance

    def add_credits(
        self,
        db: Session,
        user_id: str,
        amount: int,
        transaction_type: str = "purchase",
        description: str = "Credit purchase",
        stripe_payment_id: Optional[str] = None,
    ) -> Tuple[bool, int]:
        """
        Add credits to user's balance.

        Args:
            db: Database session
            user_id: User ID
            amount: Credits to add
            transaction_type: Type of transaction
            description: Transaction description
            stripe_payment_id: Optional Stripe payment ID

        Returns:
            Tuple of (success, new_balance)
        """
        credit = self.get_user_credits(db, user_id)
        if not credit:
            # Create credit record if doesn't exist
            credit = Credit(
                user_id=user_id,
                balance=0,
                monthly_limit=PLANS["free"].token_limit,
                used_this_period=0,
                reset_at=datetime.utcnow() + timedelta(days=30),
            )
            db.add(credit)
            db.flush()

        # Add credits
        credit.balance += amount
        new_balance = credit.balance

        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_after=new_balance,
            description=description,
            stripe_payment_id=stripe_payment_id,
        )
        db.add(transaction)

        db.commit()
        return True, new_balance

    def reset_monthly_credits(self, db: Session, user_id: str) -> Tuple[bool, int]:
        """
        Reset user's monthly credit allowance based on their plan.

        Returns:
            Tuple of (success, new_balance)
        """
        credit = self.get_user_credits(db, user_id)
        if not credit:
            return False, 0

        # Get user's subscription
        subscription = (
            db.query(Subscription).filter(Subscription.user_id == user_id).first()
        )
        plan_id = subscription.plan_id if subscription else "free"
        plan = PLANS.get(plan_id, PLANS["free"])

        # Reset credits
        credit.balance = plan.token_limit
        credit.monthly_limit = plan.token_limit
        credit.used_this_period = 0
        credit.reset_at = datetime.utcnow() + timedelta(days=30)

        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            type="subscription",
            amount=plan.token_limit,
            balance_after=credit.balance,
            description=f"Monthly credit reset ({plan.name} plan)",
        )
        db.add(transaction)

        db.commit()
        return True, credit.balance

    def _check_and_reset_monthly(self, db: Session, credit: Credit) -> None:
        """Check if monthly reset is needed and perform it."""
        if credit.reset_at and credit.reset_at <= datetime.utcnow():
            self.reset_monthly_credits(db, credit.user_id)

    def get_usage_stats(self, db: Session, user_id: str) -> dict:
        """Get usage statistics for a user."""
        credit = self.get_user_credits(db, user_id)
        if not credit:
            return {
                "balance": 0,
                "monthly_limit": 0,
                "used_this_period": 0,
                "reset_at": None,
                "percentage_used": 0,
            }

        # Check if reset is needed
        self._check_and_reset_monthly(db, credit)

        percentage = 0
        if credit.monthly_limit and credit.monthly_limit > 0:
            percentage = round(
                (credit.used_this_period / credit.monthly_limit) * 100, 1
            )

        return {
            "balance": credit.balance,
            "monthly_limit": credit.monthly_limit,
            "used_this_period": credit.used_this_period,
            "reset_at": credit.reset_at.isoformat() if credit.reset_at else None,
            "percentage_used": percentage,
        }


# Singleton instance
credit_service = CreditService()
