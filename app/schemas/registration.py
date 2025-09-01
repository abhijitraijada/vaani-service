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
