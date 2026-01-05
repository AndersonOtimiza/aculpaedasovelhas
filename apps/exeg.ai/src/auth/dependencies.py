"""
FastAPI dependencies for authentication.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_handler import verify_token, TokenData

# HTTP Bearer scheme for JWT
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials with Bearer token

    Returns:
        TokenData with user_id

    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_data = verify_token(token, token_type="access")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_active_user(
    token_data: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to get an active user (could add is_active check here).

    Args:
        token_data: Token data from get_current_user

    Returns:
        TokenData if user is active

    Raises:
        HTTPException: 403 if user is inactive
    """
    # TODO: Add database lookup to verify user is still active
    # For now, just return the token data
    return token_data


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[TokenData]:
    """
    Optional dependency - returns user data if authenticated, None otherwise.
    Useful for endpoints that work for both authenticated and anonymous users.

    Args:
        credentials: HTTP Authorization credentials (optional)

    Returns:
        TokenData if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return verify_token(token, token_type="access")
