from datetime import datetime
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user import UserService

# Security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        UserResponse: Current authenticated user
        
    Raises:
        401: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            UserService.SECRET_KEY, 
            algorithms=[UserService.ALGORITHM]
        )
        
        # Extract user information from token
        phone_number: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if phone_number is None or user_id is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is still active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return UserResponse.model_validate(user)


def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Get current active user (additional check for user status).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current active user
        
    Raises:
        401: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    return current_user
