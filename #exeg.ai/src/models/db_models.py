"""
SQLAlchemy database models for exeg.ai.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from database.init_db import Base


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    credits = relationship("Credit", back_populates="user", uselist=False)
    usage_history = relationship("UsageHistory", back_populates="user")
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class Plan(Base):
    """Subscription plan model."""
    __tablename__ = "plans"

    id = Column(String(50), primary_key=True)  # 'free', 'starter', 'pro', 'enterprise'
    name = Column(String(100), nullable=False)
    price_cents = Column(Integer, nullable=False)  # Price in cents (R$ 29.90 = 2990)
    token_limit = Column(Integer, nullable=False)  # Monthly token limit (-1 for unlimited)
    features = Column(JSON, nullable=True)  # JSON with feature flags

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscription model."""
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    plan_id = Column(String(50), ForeignKey("plans.id"), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, canceled, past_due, trialing
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")


class Credit(Base):
    """User credits (token balance) model."""
    __tablename__ = "credits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Integer, default=0)  # Current token balance
    monthly_limit = Column(Integer, nullable=True)  # Monthly limit from plan
    used_this_period = Column(Integer, default=0)  # Tokens used in current period
    reset_at = Column(DateTime, nullable=True)  # Next monthly reset date

    # Relationships
    user = relationship("User", back_populates="credits")


class UsageHistory(Base):
    """Token usage history model."""
    __tablename__ = "usage_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    endpoint = Column(String(100), nullable=False)  # '/ask', '/explain-links'
    provider = Column(String(50), nullable=False)  # 'ollama', 'openai', 'anthropic'
    model = Column(String(100), nullable=True)  # Model used
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_credits = Column(Integer, default=0)  # Credits consumed
    request_data = Column(JSON, nullable=True)  # Optional request metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_history")


class CreditTransaction(Base):
    """Credit transaction history model."""
    __tablename__ = "credit_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'purchase', 'subscription', 'bonus', 'usage', 'refund'
    amount = Column(Integer, nullable=False)  # Positive: credit, Negative: debit
    balance_after = Column(Integer, nullable=False)  # Balance after transaction
    description = Column(Text, nullable=True)
    stripe_payment_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="credit_transactions")


class APIKey(Base):
    """User API keys for BYOK (Bring Your Own Key)."""
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # 'openai', 'anthropic'
    encrypted_key = Column(Text, nullable=False)  # Fernet encrypted API key
    name = Column(String(100), nullable=True)  # User-friendly name
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="api_keys")


class PixTransaction(Base):
    """
    PIX transaction for Otimiza Pagamentos.
    Modelo Binance: usuário envia comprovante via WhatsApp para validação.
    """
    __tablename__ = "pix_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # Valor e créditos
    amount_cents = Column(Integer, nullable=False)  # Valor em centavos (R$ 29.90 = 2990)
    credits = Column(Integer, nullable=False)  # Créditos a serem carregados
    package_id = Column(String(50), nullable=True)  # Pacote comprado (small, medium, etc)

    # Dados do PIX
    pix_key = Column(String(255), nullable=False)  # Chave PIX da Otimiza
    pix_code = Column(Text, nullable=True)  # Código copia-e-cola
    qr_code_base64 = Column(Text, nullable=True)  # QR Code em base64

    # Status do pagamento
    status = Column(String(50), default="pending")  # pending, awaiting_receipt, validating, confirmed, rejected, expired

    # Comprovante enviado pelo usuário
    receipt_url = Column(Text, nullable=True)  # URL do comprovante (se enviado via API)
    receipt_whatsapp_id = Column(String(255), nullable=True)  # ID da mensagem no WhatsApp

    # Validação pela ANA (IA da Otimiza)
    validated_by = Column(String(100), nullable=True)  # 'ana_ai', 'manual'
    validation_notes = Column(Text, nullable=True)  # Notas da validação
    bank_transaction_id = Column(String(255), nullable=True)  # ID da transação bancária

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # PIX expira em 24h
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="pix_transactions")
