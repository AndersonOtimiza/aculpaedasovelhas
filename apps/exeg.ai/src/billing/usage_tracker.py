"""
Usage tracking service for exeg.ai.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.db_models import UsageHistory
from .plans import calculate_credits
from .credit_service import credit_service


class UsageTracker:
    """Service for tracking API usage and token consumption."""

    def record_usage(
        self,
        db: Session,
        user_id: str,
        endpoint: str,
        provider: str,
        model: Optional[str],
        input_tokens: int,
        output_tokens: int,
        request_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record API usage and deduct credits.

        Args:
            db: Database session
            user_id: User ID
            endpoint: API endpoint used
            provider: LLM provider
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            request_data: Optional request metadata

        Returns:
            Dict with usage info and credit status
        """
        total_tokens = input_tokens + output_tokens
        credits_cost = calculate_credits(provider, model, total_tokens)

        # Deduct credits
        success, new_balance = credit_service.deduct_credits(
            db,
            user_id,
            credits_cost,
            description=f"{endpoint} - {provider}/{model or 'default'} ({total_tokens} tokens)",
        )

        if not success:
            return {
                "success": False,
                "error": "Insufficient credits",
                "balance": new_balance,
                "required": credits_cost,
            }

        # Record usage
        usage = UsageHistory(
            user_id=user_id,
            endpoint=endpoint,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_credits=credits_cost,
            request_data=request_data,
        )
        db.add(usage)
        db.commit()

        return {
            "success": True,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "credits_used": credits_cost,
            },
            "balance": new_balance,
        }

    def get_user_usage(
        self,
        db: Session,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[UsageHistory]:
        """
        Get usage history for a user.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum records to return
            offset: Records to skip
            start_date: Filter from this date
            end_date: Filter until this date

        Returns:
            List of usage records
        """
        query = db.query(UsageHistory).filter(UsageHistory.user_id == user_id)

        if start_date:
            query = query.filter(UsageHistory.created_at >= start_date)
        if end_date:
            query = query.filter(UsageHistory.created_at <= end_date)

        return (
            query.order_by(UsageHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_usage_summary(
        self,
        db: Session,
        user_id: str,
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get usage summary for a period.

        Args:
            db: Database session
            user_id: User ID
            period_days: Number of days to summarize

        Returns:
            Summary with totals and breakdowns
        """
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Get usage records for the period
        records = (
            db.query(UsageHistory)
            .filter(UsageHistory.user_id == user_id)
            .filter(UsageHistory.created_at >= start_date)
            .all()
        )

        if not records:
            return {
                "period_start": start_date.isoformat(),
                "period_end": datetime.utcnow().isoformat(),
                "total_requests": 0,
                "total_tokens": 0,
                "total_credits": 0,
                "by_provider": {},
                "by_endpoint": {},
                "by_day": [],
            }

        # Aggregate stats
        total_requests = len(records)
        total_tokens = sum(r.total_tokens for r in records)
        total_credits = sum(r.cost_credits for r in records)

        # Group by provider
        by_provider = {}
        for r in records:
            if r.provider not in by_provider:
                by_provider[r.provider] = {
                    "requests": 0,
                    "tokens": 0,
                    "credits": 0,
                }
            by_provider[r.provider]["requests"] += 1
            by_provider[r.provider]["tokens"] += r.total_tokens
            by_provider[r.provider]["credits"] += r.cost_credits

        # Group by endpoint
        by_endpoint = {}
        for r in records:
            if r.endpoint not in by_endpoint:
                by_endpoint[r.endpoint] = {
                    "requests": 0,
                    "tokens": 0,
                    "credits": 0,
                }
            by_endpoint[r.endpoint]["requests"] += 1
            by_endpoint[r.endpoint]["tokens"] += r.total_tokens
            by_endpoint[r.endpoint]["credits"] += r.cost_credits

        # Group by day
        by_day = {}
        for r in records:
            day = r.created_at.strftime("%Y-%m-%d")
            if day not in by_day:
                by_day[day] = {
                    "date": day,
                    "requests": 0,
                    "tokens": 0,
                    "credits": 0,
                }
            by_day[day]["requests"] += 1
            by_day[day]["tokens"] += r.total_tokens
            by_day[day]["credits"] += r.cost_credits

        return {
            "period_start": start_date.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_credits": total_credits,
            "by_provider": by_provider,
            "by_endpoint": by_endpoint,
            "by_day": sorted(by_day.values(), key=lambda x: x["date"]),
        }

    def estimate_cost(
        self,
        provider: str,
        model: Optional[str],
        estimated_tokens: int,
    ) -> int:
        """
        Estimate credit cost for a request.

        Args:
            provider: LLM provider
            model: Model name
            estimated_tokens: Estimated total tokens

        Returns:
            Estimated credits required
        """
        return calculate_credits(provider, model, estimated_tokens)


# Singleton instance
usage_tracker = UsageTracker()
