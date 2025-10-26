import uuid
import bcrypt
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import (
    UserCreate, UserResponse, TokenResponse, 
    ChangePasswordRequest, UserUpdateRequest, PasswordChangeResponse
)
from app.schemas.enums import UserType


class UserService:
    """Service class for user-related operations"""
    
    # JWT Configuration
    SECRET_KEY = "your-secret-key-change-in-production"  # In production, use environment variable
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 300  # 5 hours
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=UserService.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, UserService.SECRET_KEY, algorithm=UserService.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        """Create a new user with Organiser type"""
        try:
            # Check if phone number already exists
            existing_user = db.query(User).filter(User.phone_number == user_data.phone_number).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered"
                )
            
            # Hash the password
            hashed_password = UserService.hash_password(user_data.password)
            
            # Create user with Organiser type
            db_user = User(
                id=str(uuid.uuid4()),
                phone_number=user_data.phone_number,
                password_hash=hashed_password,
                name=user_data.name,
                email=user_data.email,
                user_type=UserType.ORGANISER,  # Only create Organiser users
                is_active=True
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return UserResponse.model_validate(db_user)
            
        except IntegrityError as e:
            db.rollback()
            if "phone_number" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    @staticmethod
    def get_user_by_phone(db: Session, phone_number: str) -> User:
        """Get user by phone number"""
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def authenticate_user(db: Session, phone_number: str, password: str) -> User:
        """Authenticate user with phone number and password"""
        user = UserService.get_user_by_phone(db, phone_number)
        
        if not UserService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user
    
    @staticmethod
    def login_user(db: Session, phone_number: str, password: str) -> TokenResponse:
        """Authenticate user and return JWT token"""
        # Authenticate user
        user = UserService.authenticate_user(db, phone_number, password)
        
        # Create access token
        access_token_expires = timedelta(minutes=UserService.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = UserService.create_access_token(
            data={"sub": user.phone_number, "user_id": user.id, "user_type": user.user_type.value},
            expires_delta=access_token_expires
        )
        
        # Create user response
        user_response = UserResponse.model_validate(user)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: str, 
        password_data: ChangePasswordRequest
    ) -> PasswordChangeResponse:
        """Change user password"""
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify current password
            if not UserService.verify_password(password_data.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_password_hash = UserService.hash_password(password_data.new_password)
            
            # Update password
            user.password_hash = new_password_hash
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            return PasswordChangeResponse(message="Password changed successfully")
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to change password: {str(e)}"
            )
    
    @staticmethod
    def update_user(
        db: Session, 
        user_id: str, 
        update_data: UserUpdateRequest
    ) -> UserResponse:
        """Update user information"""
        try:
            # Get user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields if provided
            if update_data.name is not None:
                user.name = update_data.name
            
            if update_data.email is not None:
                user.email = update_data.email
            
            user.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(user)
            
            return UserResponse.model_validate(user)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
