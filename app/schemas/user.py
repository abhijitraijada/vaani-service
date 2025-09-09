from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from app.schemas.enums import UserType


class UserCreate(BaseModel):
    """Schema for creating a new user (Organiser only)"""
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number for login")
    password: str = Field(..., min_length=6, description="Password for authentication")
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "password": "securepassword123",
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response data"""
    id: str
    phone_number: str
    name: str
    email: Optional[str] = None
    user_type: UserType
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "phone_number": "+1234567890",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "user_type": "organiser",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    phone_number: str = Field(..., description="Phone number for login")
    password: str = Field(..., description="Password for authentication")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "phone_number": "+1234567890",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "user_type": "organiser",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password"""
    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=6, description="New password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword456"
            }
        }


class UserUpdateRequest(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Name",
                "email": "updated.email@example.com"
            }
        }


class PasswordChangeResponse(BaseModel):
    """Schema for password change response"""
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password changed successfully"
            }
        }
