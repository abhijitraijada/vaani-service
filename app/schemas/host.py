from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.enums import ToiletFacilities, GenderPreference


class HostCreate(BaseModel):
    """Schema for creating a new host"""
    event_id: str = Field(..., description="Event ID this host belongs to")
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
    name: str
    phone_no: int
    place_name: str
    max_participants: int
    toilet_facilities: ToiletFacilities
    gender_preference: GenderPreference
    facilities_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "event_id": "456e7890-e89b-12d3-a456-426614174001",
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
        }


class HostCSVRow(BaseModel):
    """Schema for CSV row validation"""
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
                "name": "John",
                "min_capacity": 3,
                "max_capacity": 10,
                "toilet_facilities": "both",
                "gender_preference": "both",
                "has_facilities_description": True
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
