from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.enums import (
    RegistrationType,
    TransportationMode,
    Gender,
    RegistrationStatus,
    ToiletPreference
)


class DailyPreferenceCreate(BaseModel):
    event_day_id: str
    staying_with_yatra: Optional[bool] = True
    dinner_at_host: Optional[bool] = True
    breakfast_at_host: Optional[bool] = True
    lunch_with_yatra: Optional[bool] = True
    physical_limitations: Optional[str] = None
    toilet_preference: Optional[ToiletPreference] = ToiletPreference.INDIAN


class DailyPreferenceResponse(DailyPreferenceCreate):
    id: str
    registration_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventDayInfo(BaseModel):
    """Event day information for daily preferences"""
    id: str
    event_date: Optional[date] = None
    location_name: Optional[str] = None
    breakfast_provided: Optional[bool] = None
    lunch_provided: Optional[bool] = None
    dinner_provided: Optional[bool] = None
    daily_notes: Optional[str] = None

    class Config:
        from_attributes = True


class DailyPreferenceWithEventDayResponse(DailyPreferenceResponse):
    event_day: Optional[EventDayInfo] = None

    class Config:
        from_attributes = True


class DailyScheduleItem(BaseModel):
    """Merged daily schedule combining event day info with user preferences"""
    # Event Day Information
    event_day_id: str
    event_date: Optional[date] = None
    location_name: Optional[str] = None
    breakfast_provided: Optional[bool] = None
    lunch_provided: Optional[bool] = None
    dinner_provided: Optional[bool] = None
    daily_notes: Optional[str] = None
    
    # User Preferences for this day
    preference_id: Optional[str] = None
    staying_with_yatra: Optional[bool] = True
    dinner_at_host: Optional[bool] = True
    breakfast_at_host: Optional[bool] = True
    lunch_with_yatra: Optional[bool] = True
    physical_limitations: Optional[str] = None
    toilet_preference: Optional[ToiletPreference] = ToiletPreference.INDIAN
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegistrationMemberCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Gender
    language: Optional[str] = None
    floor_preference: Optional[str] = None
    special_requirements: Optional[str] = None
    status: Optional[RegistrationStatus] = RegistrationStatus.REGISTERED


class RegistrationMemberResponse(RegistrationMemberCreate):
    id: str
    registration_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegistrationMemberUpdate(BaseModel):
    """Schema for updating registration member information"""
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Member's name")
    email: Optional[str] = Field(None, description="Member's email")
    city: Optional[str] = Field(None, max_length=100, description="Member's city")
    age: Optional[int] = Field(None, ge=1, le=120, description="Member's age")
    language: Optional[str] = Field(None, max_length=50, description="Preferred language")
    floor_preference: Optional[str] = Field(None, max_length=100, description="Floor preference")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    status: Optional[RegistrationStatus] = Field(None, description="Registration status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Name",
                "email": "updated@example.com",
                "city": "Updated City",
                "age": 30,
                "language": "English",
                "floor_preference": "Ground floor",
                "special_requirements": "Updated requirements",
                "status": "confirmed"
            }
        }


class RegistrationMemberStatusUpdate(BaseModel):
    """Schema for updating only the registration status"""
    status: RegistrationStatus = Field(..., description="New registration status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "confirmed"
            }
        }


class RegistrationCreate(BaseModel):
    event_id: str
    registration_type: RegistrationType
    number_of_members: int
    transportation_mode: TransportationMode
    has_empty_seats: Optional[bool] = False
    available_seats_count: Optional[int] = 0
    notes: Optional[str] = None
    members: List[RegistrationMemberCreate]
    daily_preferences: List[DailyPreferenceCreate]


class RegistrationResponse(BaseModel):
    id: int
    event_id: str
    registration_type: RegistrationType
    number_of_members: int
    transportation_mode: TransportationMode
    has_empty_seats: Optional[bool]
    available_seats_count: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    members: List[RegistrationMemberResponse]
    daily_preferences: List[DailyPreferenceResponse]

    class Config:
        from_attributes = True


class ParticipantSearchResponse(BaseModel):
    """Comprehensive response for participant search by phone number"""
    registration_id: int
    event_id: str
    registration_type: RegistrationType
    transportation_mode: TransportationMode
    has_empty_seats: Optional[bool]
    available_seats_count: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # All members in the registration (including the searched participant)
    members: List[RegistrationMemberResponse]
    
    # Merged daily schedule combining event days with user preferences
    daily_schedule: List[DailyScheduleItem]

    class Config:
        from_attributes = True
