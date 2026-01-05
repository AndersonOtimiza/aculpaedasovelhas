"""
Pydantic models for user-related requests and responses.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


# ============================================================
# Request Models
# ============================================================

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: Optional[str] = Field(None, max_length=100)

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User profile update request."""
    name: Optional[str] = Field(None, max_length=100)
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)


class PasswordReset(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================
# Response Models
# ============================================================

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class AuthResponse(BaseModel):
    """Authentication response with user and tokens."""
    success: bool
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    """Simple message response."""
    success: bool
    message: str


# ============================================================
# API Key Models
# ============================================================

class APIKeyCreate(BaseModel):
    """Create API key request (BYOK)."""
    provider: str = Field(..., pattern="^(openai|anthropic)$")
    api_key: str = Field(..., min_length=10)
    name: Optional[str] = Field(None, max_length=100)


class APIKeyResponse(BaseModel):
    """API key response (key is masked)."""
    id: str
    provider: str
    name: Optional[str]
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    masked_key: str  # e.g., "sk-...abc123"

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """List of API keys."""
    success: bool
    data: List[APIKeyResponse]


# ============================================================
# User Profile with Billing
# ============================================================

class CreditInfo(BaseModel):
    """User credit information."""
    balance: int
    monthly_limit: Optional[int]
    used_this_period: int
    reset_at: Optional[datetime]

    class Config:
        from_attributes = True


class SubscriptionInfo(BaseModel):
    """User subscription information."""
    plan_id: str
    plan_name: str
    status: str
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Complete user profile with billing info."""
    success: bool
    user: UserResponse
    credits: Optional[CreditInfo]
    subscription: Optional[SubscriptionInfo]
