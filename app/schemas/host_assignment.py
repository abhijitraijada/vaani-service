from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class HostAssignmentCreate(BaseModel):
    """Schema for creating a new host assignment"""
    host_id: str = Field(..., description="ID of the host")
    registration_member_id: str = Field(..., description="ID of the registration member")
    event_day_id: str = Field(..., description="ID of the event day")
    assignment_notes: Optional[str] = Field(None, description="Assignment notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "host_id": "123e4567-e89b-12d3-a456-426614174000",
                "registration_member_id": "456e7890-e89b-12d3-a456-426614174001",
                "event_day_id": "789e0123-e89b-12d3-a456-426614174002",
                "assignment_notes": "Special dietary requirements"
            }
        }


class HostAssignmentUpdate(BaseModel):
    """Schema for updating host assignment information"""
    assignment_notes: Optional[str] = Field(None, description="Assignment notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_notes": "Updated assignment notes"
            }
        }


class HostAssignmentResponse(BaseModel):
    """Schema for host assignment response data"""
    id: str
    host_id: str
    registration_member_id: str
    event_day_id: str
    assignment_notes: Optional[str] = None
    assigned_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "host_id": "456e7890-e89b-12d3-a456-426614174001",
                "registration_member_id": "789e0123-e89b-12d3-a456-426614174002",
                "event_day_id": "012e3456-e89b-12d3-a456-426614174003",
                "assignment_notes": "Special dietary requirements",
                "assigned_by": "345e6789-e89b-12d3-a456-426614174004",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class HostAssignmentFilterParams(BaseModel):
    """Schema for host assignment filtering parameters"""
    host_id: Optional[str] = Field(None, description="Filter by host ID")
    registration_member_id: Optional[str] = Field(None, description="Filter by registration member ID")
    event_day_id: Optional[str] = Field(None, description="Filter by event day ID")
    assigned_by: Optional[str] = Field(None, description="Filter by who made the assignment")
    has_notes: Optional[bool] = Field(None, description="Filter assignments with/without notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "host_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_day_id": "456e7890-e89b-12d3-a456-426614174001",
                "has_notes": True
            }
        }


class HostAssignmentListResponse(BaseModel):
    """Schema for paginated host assignment list response"""
    assignments: List[HostAssignmentResponse] = Field(..., description="List of host assignments")
    total_count: int = Field(..., description="Total number of assignments matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of assignments per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignments": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "host_id": "456e7890-e89b-12d3-a456-426614174001",
                        "registration_member_id": "789e0123-e89b-12d3-a456-426614174002",
                        "event_day_id": "012e3456-e89b-12d3-a456-426614174003",
                        "assignment_notes": "Special dietary requirements",
                        "assigned_by": "345e6789-e89b-12d3-a456-426614174004",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total_count": 25,
                "page": 1,
                "page_size": 10,
                "total_pages": 3
            }
        }


class HostAssignmentDeleteResponse(BaseModel):
    """Schema for host assignment deletion response"""
    message: str = Field(..., description="Success message")
    deleted_assignment_id: str = Field(..., description="ID of the deleted assignment")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Host assignment deleted successfully",
                "deleted_assignment_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
