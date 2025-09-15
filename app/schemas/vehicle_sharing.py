from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class VehicleSharingCreate(BaseModel):
    """Schema for creating a new vehicle sharing arrangement"""
    vehicle_owner_member_id: str = Field(..., description="ID of the vehicle owner (registration member)")
    co_traveler_member_id: str = Field(..., description="ID of the co-traveler (registration member)")
    sharing_notes: Optional[str] = Field(None, description="Sharing arrangement notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_owner_member_id": "123e4567-e89b-12d3-a456-426614174000",
                "co_traveler_member_id": "456e7890-e89b-12d3-a456-426614174001",
                "sharing_notes": "Pick up from downtown at 8 AM"
            }
        }


class VehicleSharingUpdate(BaseModel):
    """Schema for updating vehicle sharing information"""
    sharing_notes: Optional[str] = Field(None, description="Sharing arrangement notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sharing_notes": "Updated pickup location and time"
            }
        }


class VehicleSharingResponse(BaseModel):
    """Schema for vehicle sharing response data"""
    id: str
    vehicle_owner_member_id: str
    co_traveler_member_id: str
    sharing_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "vehicle_owner_member_id": "456e7890-e89b-12d3-a456-426614174001",
                "co_traveler_member_id": "789e0123-e89b-12d3-a456-426614174002",
                "sharing_notes": "Pick up from downtown at 8 AM",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class VehicleSharingFilterParams(BaseModel):
    """Schema for vehicle sharing filtering parameters"""
    vehicle_owner_member_id: Optional[str] = Field(None, description="Filter by vehicle owner member ID")
    co_traveler_member_id: Optional[str] = Field(None, description="Filter by co-traveler member ID")
    has_notes: Optional[bool] = Field(None, description="Filter arrangements with/without notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_owner_member_id": "123e4567-e89b-12d3-a456-426614174000",
                "has_notes": True
            }
        }


class VehicleSharingListResponse(BaseModel):
    """Schema for paginated vehicle sharing list response"""
    arrangements: List[VehicleSharingResponse] = Field(..., description="List of vehicle sharing arrangements")
    total_count: int = Field(..., description="Total number of arrangements matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of arrangements per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "arrangements": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "vehicle_owner_member_id": "456e7890-e89b-12d3-a456-426614174001",
                        "co_traveler_member_id": "789e0123-e89b-12d3-a456-426614174002",
                        "sharing_notes": "Pick up from downtown at 8 AM",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total_count": 15,
                "page": 1,
                "page_size": 10,
                "total_pages": 2
            }
        }


class VehicleSharingDeleteResponse(BaseModel):
    """Schema for vehicle sharing deletion response"""
    message: str = Field(..., description="Success message")
    deleted_arrangement_id: str = Field(..., description="ID of the deleted arrangement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Vehicle sharing arrangement deleted successfully",
                "deleted_arrangement_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
