from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.enums import ToiletFacilities, GenderPreference, Gender


class ParticipantSummary(BaseModel):
    """Lightweight participant data for host responses"""
    id: str = Field(..., description="Participant ID")
    assignment_id: str = Field(..., description="Host assignment ID")
    name: str = Field(..., description="Participant name")
    phone_number: str = Field(..., description="Participant phone number")
    age: Optional[int] = Field(None, description="Participant age")
    gender: Optional[Gender] = Field(None, description="Participant gender")
    city: Optional[str] = Field(None, description="Participant city")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    assignment_notes: Optional[str] = Field(None, description="Assignment-specific notes")
    assigned_at: datetime = Field(..., description="When participant was assigned to host")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "assignment_id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "Rajesh Kumar",
                "phone_number": "9876543210",
                "age": 35,
                "gender": "M",
                "city": "Ahmedabad",
                "special_requirements": "Vegetarian meals",
                "assignment_notes": "Ground floor preference",
                "assigned_at": "2024-01-15T10:30:00Z"
            }
        }


class HostCreate(BaseModel):
    """Schema for creating a new host"""
    event_id: str = Field(..., description="Event ID this host belongs to")
    event_days_id: str = Field(..., description="Event day ID this host belongs to")
    name: str = Field(..., min_length=2, max_length=255, description="Host's name")
    phone_no: int = Field(..., description="Host's phone number")
    place_name: str = Field(..., min_length=2, max_length=255, description="Location/place name")
    max_participants: int = Field(..., gt=0, description="Maximum participants capacity")
    toilet_facilities: ToiletFacilities = Field(..., description="Available toilet facilities")
    gender_preference: GenderPreference = Field(..., description="Gender preference for participants")
    facilities_description: Optional[str] = Field(None, description="Additional facilities description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_days_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                "name": "John Smith",
                "phone_no": 9876543210,
                "place_name": "Smith Residence, Downtown",
                "max_participants": 5,
                "toilet_facilities": "both",
                "gender_preference": "both",
                "facilities_description": "Air conditioning, WiFi, parking available"
            }
        }


class HostUpdate(BaseModel):
    """Schema for updating host information"""
    event_days_id: Optional[str] = Field(None, description="Event day ID this host belongs to")
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Host's name")
    phone_no: Optional[int] = Field(None, description="Host's phone number")
    place_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Location/place name")
    max_participants: Optional[int] = Field(None, gt=0, description="Maximum participants capacity")
    toilet_facilities: Optional[ToiletFacilities] = Field(None, description="Available toilet facilities")
    gender_preference: Optional[GenderPreference] = Field(None, description="Gender preference for participants")
    facilities_description: Optional[str] = Field(None, description="Additional facilities description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_days_id": "cfa43dc7-b86d-4006-aad6-c78d5dff4dce",
                "name": "Updated Host Name",
                "phone_no": 9876543211,
                "place_name": "Updated Location",
                "max_participants": 8,
                "toilet_facilities": "western",
                "gender_preference": "female",
                "facilities_description": "Updated facilities description"
            }
        }


class HostResponse(BaseModel):
    """Schema for host response data"""
    id: str
    event_id: str
    event_days_id: Optional[str] = None
    event_date: Optional[date] = None
    name: str
    phone_no: int
    place_name: str
    max_participants: int
    toilet_facilities: ToiletFacilities
    gender_preference: GenderPreference
    facilities_description: Optional[str] = None
    assigned_participants: List[ParticipantSummary] = Field(default_factory=list, description="List of assigned participants")
    current_capacity: int = Field(..., description="Current number of assigned participants")
    available_capacity: int = Field(..., description="Available capacity (max_participants - current_capacity)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "event_id": "456e7890-e89b-12d3-a456-426614174001",
                "event_days_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                "event_date": "2024-10-31",
                "name": "John Smith",
                "phone_no": 9876543210,
                "place_name": "Smith Residence, Downtown",
                "max_participants": 5,
                "toilet_facilities": "both",
                "gender_preference": "both",
                "facilities_description": "Air conditioning, WiFi, parking available",
                "assigned_participants": [
                    {
                        "id": "456e7890-e89b-12d3-a456-426614174001",
                        "assignment_id": "789e0123-e89b-12d3-a456-426614174002",
                        "name": "Rajesh Kumar",
                        "phone_number": "9876543210",
                        "age": 35,
                        "gender": "M",
                        "city": "Ahmedabad",
                        "special_requirements": "Vegetarian meals",
                        "assignment_notes": "Ground floor preference",
                        "assigned_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "current_capacity": 1,
                "available_capacity": 4,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class HostCSVRow(BaseModel):
    """Schema for CSV row validation"""
    event_days_id: str = Field(..., description="Event day ID this host belongs to")
    name: str = Field(..., min_length=2, max_length=255, description="Host's name")
    phone_no: int = Field(..., description="Host's phone number")
    place_name: str = Field(..., min_length=2, max_length=255, description="Location/place name")
    max_participants: int = Field(..., gt=0, description="Maximum participants capacity")
    toilet_facilities: ToiletFacilities = Field(..., description="Available toilet facilities")
    gender_preference: GenderPreference = Field(..., description="Gender preference for participants")
    facilities_description: Optional[str] = Field(None, description="Additional facilities description")


class HostCSVUpload(BaseModel):
    """Schema for CSV upload response"""
    total_rows: int = Field(..., description="Total number of rows processed")
    successful_imports: int = Field(..., description="Number of successfully imported hosts")
    failed_imports: int = Field(..., description="Number of failed imports")
    errors: List[str] = Field(..., description="List of error messages for failed imports")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_rows": 10,
                "successful_imports": 8,
                "failed_imports": 2,
                "errors": [
                    "Row 3: Invalid phone number format",
                    "Row 7: Invalid toilet facilities value"
                ]
            }
        }


class HostDeleteResponse(BaseModel):
    """Schema for host deletion response"""
    message: str = Field(..., description="Success message")
    deleted_host_id: str = Field(..., description="ID of the deleted host")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Host deleted successfully",
                "deleted_host_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class HostFilterParams(BaseModel):
    """Schema for host filtering parameters"""
    event_id: Optional[str] = Field(None, description="Filter by event ID")
    event_days_id: Optional[str] = Field(None, description="Filter by event day ID")
    name: Optional[str] = Field(None, description="Filter by host name (partial match)")
    phone_no: Optional[int] = Field(None, description="Filter by exact phone number")
    place_name: Optional[str] = Field(None, description="Filter by place name (partial match)")
    min_capacity: Optional[int] = Field(None, ge=1, description="Minimum capacity filter")
    max_capacity: Optional[int] = Field(None, ge=1, description="Maximum capacity filter")
    toilet_facilities: Optional[ToiletFacilities] = Field(None, description="Filter by toilet facilities")
    gender_preference: Optional[GenderPreference] = Field(None, description="Filter by gender preference")
    has_facilities_description: Optional[bool] = Field(None, description="Filter hosts with/without facilities description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_days_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                "name": "John",
                "min_capacity": 3,
                "max_capacity": 10,
                "toilet_facilities": "both",
                "gender_preference": "both",
                "has_facilities_description": True
            }
        }


class HostsByEventDayResponse(BaseModel):
    """Schema for hosts grouped by event day"""
    event_date: date = Field(..., description="Event date")
    event_day_id: str = Field(..., description="Event day ID")
    hosts: List[HostResponse] = Field(..., description="List of hosts for this event day")
    total_hosts: int = Field(..., description="Total number of hosts for this event day")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_date": "2024-10-31",
                "event_day_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                "hosts": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "event_id": "456e7890-e89b-12d3-a456-426614174001",
                        "event_days_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                        "event_date": "2024-10-31",
                        "name": "John Smith",
                        "phone_no": 9876543210,
                        "place_name": "Monpur",
                        "max_participants": 5,
                        "toilet_facilities": "both",
                        "gender_preference": "both",
                        "facilities_description": "Air conditioning, WiFi, parking available",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total_hosts": 15
            }
        }


class HostsByEventResponse(BaseModel):
    """Schema for hosts grouped by event days"""
    event_id: str = Field(..., description="Event ID")
    event_days: List[HostsByEventDayResponse] = Field(..., description="Hosts grouped by event days")
    total_hosts: int = Field(..., description="Total number of hosts across all event days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_days": [
                    {
                        "event_date": "2024-10-31",
                        "event_day_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                        "hosts": [],
                        "total_hosts": 15
                    },
                    {
                        "event_date": "2024-11-01",
                        "event_day_id": "cfa43dc7-b86d-4006-aad6-c78d5dff4dce",
                        "hosts": [],
                        "total_hosts": 12
                    }
                ],
                "total_hosts": 27
            }
        }


class HostListResponse(BaseModel):
    """Schema for paginated host list response"""
    hosts: List[HostResponse] = Field(..., description="List of hosts")
    total_count: int = Field(..., description="Total number of hosts matching filters")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of hosts per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "hosts": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "event_id": "456e7890-e89b-12d3-a456-426614174001",
                        "event_days_id": "1df9ffc6-fcf4-4c71-861f-0dc54c96c7a2",
                        "event_date": "2024-10-31",
                        "name": "John Smith",
                        "phone_no": 9876543210,
                        "place_name": "Smith Residence, Downtown",
                        "max_participants": 5,
                        "toilet_facilities": "both",
                        "gender_preference": "both",
                        "facilities_description": "Air conditioning, WiFi, parking available",
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
