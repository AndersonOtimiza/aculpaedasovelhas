"""
Authentication routes for exeg.ai.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.init_db import get_db
from src.auth.password import verify_password, get_password_hash
from src.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from src.auth.dependencies import get_current_user, TokenData
from src.models.db_models import User, Credit, Subscription
from src.models.user import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest,
    UserResponse,
    TokenResponse,
    AuthResponse,
    MessageResponse,
)
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserRegister) -> User:
    """Create a new user with free plan."""
    # Create user
    user = User(
        email=user_data.email.lower(),
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
    )
    db.add(user)
    db.flush()  # Get user.id

    # Create credit record with free plan limits
    credit = Credit(
        user_id=user.id,
        balance=10000,  # Free plan: 10k tokens
        monthly_limit=10000,
        used_this_period=0,
        reset_at=datetime.utcnow() + timedelta(days=30),
    )
    db.add(credit)

    # Create subscription with free plan
    subscription = Subscription(
        user_id=user.id,
        plan_id="free",
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
    )
    db.add(subscription)

    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.

    Creates user with free plan (10,000 tokens/month).
    """
    # Check if user exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = create_user(db, user_data)

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return AuthResponse(
        success=True,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns JWT access and refresh tokens.
    """
    # Find user
    user = get_user_by_email(db, credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return AuthResponse(
        success=True,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
        ),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token
    token_data = verify_token(request.refresh_token, token_type="refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify user still exists and is active
    user = get_user_by_id(db, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Generate new tokens
    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(token_data: TokenData = Depends(get_current_user)):
    """
    Logout current user.

    Note: With JWT, logout is handled client-side by deleting tokens.
    This endpoint is provided for API completeness.
    """
    # In a production system, you might want to:
    # - Add the token to a blacklist (Redis)
    # - Invalidate all user sessions
    # For now, just return success
    return MessageResponse(
        success=True,
        message="Logged out successfully",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user information.
    """
    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )
