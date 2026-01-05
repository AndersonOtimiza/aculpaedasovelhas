"""
Database initialization and session management.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from src.config.settings import settings

# Ensure database directory exists
db_path = Path("./database")
db_path.mkdir(exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency to get a database session.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """
    Initialize the database by creating all tables.
    Should be called on application startup.
    """
    # Import all models to ensure they are registered with Base
    from src.models import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def seed_plans() -> None:
    """
    Seed the database with default subscription plans.
    """
    from src.models.db_models import Plan

    db = SessionLocal()
    try:
        # Check if plans already exist
        existing = db.query(Plan).first()
        if existing:
            print("Plans already seeded")
            return

        plans = [
            Plan(
                id="free",
                name="Free",
                price_cents=0,
                token_limit=10000,
                features={
                    "providers": ["ollama"],
                    "support": "community",
                    "api_access": True,
                },
            ),
            Plan(
                id="starter",
                name="Starter",
                price_cents=2990,
                token_limit=100000,
                features={
                    "providers": ["ollama", "openai", "anthropic"],
                    "support": "email",
                    "api_access": True,
                    "priority": False,
                },
            ),
            Plan(
                id="pro",
                name="Pro",
                price_cents=9990,
                token_limit=500000,
                features={
                    "providers": ["ollama", "openai", "anthropic"],
                    "support": "priority",
                    "api_access": True,
                    "priority": True,
                    "byok": False,
                },
            ),
            Plan(
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
                },
            ),
        ]

        for plan in plans:
            db.add(plan)

        db.commit()
        print("Plans seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"Error seeding plans: {e}")
    finally:
        db.close()
