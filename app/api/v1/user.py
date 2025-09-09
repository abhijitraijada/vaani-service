from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.user import (
    UserCreate, UserResponse, UserLogin, TokenResponse,
    ChangePasswordRequest, UserUpdateRequest, PasswordChangeResponse
)
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new user with Organiser type (Requires Authentication).
    
    This endpoint creates a new user account with the following characteristics:
    - User type is automatically set to 'organiser'
    - Phone number must be unique
    - Password is hashed using bcrypt
    - User is created in active state
    - Requires valid JWT token in Authorization header
    
    Args:
        user_data: User creation data including phone_number, password, name, and optional email
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        UserResponse: Created user information (password hash is not included)
        
    Raises:
        401: If authentication token is invalid or missing
        400: If phone number already exists or validation fails
        500: If internal server error occurs
    """
    return UserService.create_user(db, user_data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    This endpoint authenticates a user with their phone number and password,
    then returns a JWT access token for subsequent API requests.
    
    Args:
        login_data: User login credentials (phone_number and password)
        
    Returns:
        TokenResponse: JWT access token and user information
        
    Raises:
        401: If credentials are invalid or user is inactive
        404: If user is not found
    """
    return UserService.login_user(db, login_data.phone_number, login_data.password)


@router.put("/change-password", response_model=PasswordChangeResponse, status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Change user password (Requires Authentication).
    
    This endpoint allows authenticated users to change their password.
    The user must provide their current password for verification.
    
    Args:
        password_data: Current and new password information
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        PasswordChangeResponse: Success message
        
    Raises:
        401: If authentication token is invalid or missing
        400: If current password is incorrect
        404: If user is not found
        500: If internal server error occurs
    """
    return UserService.change_password(db, current_user.id, password_data)


@router.put("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update user information (Requires Authentication).
    
    This endpoint allows authenticated users to update their profile information.
    Only name and email can be updated. Phone number and user type cannot be changed.
    
    Args:
        update_data: User information to update (name and/or email)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        UserResponse: Updated user information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If user is not found
        500: If internal server error occurs
    """
    return UserService.update_user(db, current_user.id, update_data)
