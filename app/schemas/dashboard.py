from datetime import datetime, date
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.enums import (
    RegistrationType,
    TransportationMode,
    Gender,
    RegistrationStatus,
    ToiletPreference
)


class DailyPreferenceInfo(BaseModel):
    """Daily preference information for dashboard"""
    id: str
    event_day_id: str
    staying_with_yatra: Optional[bool] = True
    dinner_at_host: Optional[bool] = True
    breakfast_at_host: Optional[bool] = True
    lunch_with_yatra: Optional[bool] = True
    physical_limitations: Optional[str] = None
    toilet_preference: Optional[ToiletPreference] = ToiletPreference.INDIAN
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventDayInfo(BaseModel):
    """Event day information for dashboard"""
    id: str
    event_date: Optional[date] = None
    location_name: Optional[str] = None
    breakfast_provided: Optional[bool] = None
    lunch_provided: Optional[bool] = None
    dinner_provided: Optional[bool] = None
    daily_notes: Optional[str] = None

    class Config:
        from_attributes = True


class RegistrationMemberInfo(BaseModel):
    """Registration member information for dashboard"""
    id: str
    name: str
    phone_number: str
    email: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Gender
    language: Optional[str] = None
    floor_preference: Optional[str] = None
    special_requirements: Optional[str] = None
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegistrationGroupInfo(BaseModel):
    """Registration group information for dashboard"""
    id: int
    registration_type: RegistrationType
    number_of_members: int
    transportation_mode: TransportationMode
    has_empty_seats: Optional[bool] = False
    available_seats_count: Optional[int] = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    members: List[RegistrationMemberInfo]
    daily_preferences: List[DailyPreferenceInfo]

    class Config:
        from_attributes = True


class ParticipantWithPreferences(BaseModel):
    """Participant with all details including preferences and group info"""
    # Member details
    id: str
    name: str
    phone_number: str
    email: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Gender
    language: Optional[str] = None
    floor_preference: Optional[str] = None
    special_requirements: Optional[str] = None
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime
    
    # Daily preference details
    staying_with_yatra: Optional[bool] = True
    dinner_at_host: Optional[bool] = True
    breakfast_at_host: Optional[bool] = True
    lunch_with_yatra: Optional[bool] = True
    physical_limitations: Optional[str] = None
    toilet_preference: Optional[ToiletPreference] = ToiletPreference.INDIAN
    
    # Group/Registration details
    group_id: int
    registration_type: RegistrationType
    transportation_mode: TransportationMode
    has_empty_seats: Optional[bool] = False
    available_seats_count: Optional[int] = 0
    notes: Optional[str] = None
    
    # Host assignment details (if assigned)
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    host_place_name: Optional[str] = None
    host_phone_no: Optional[int] = None

    class Config:
        from_attributes = True


class DailyScheduleItem(BaseModel):
    """Daily schedule item with participants for that day"""
    event_day_id: str
    event_date: Optional[date] = None
    location_name: Optional[str] = None
    breakfast_provided: Optional[bool] = None
    lunch_provided: Optional[bool] = None
    dinner_provided: Optional[bool] = None
    daily_notes: Optional[str] = None
    
    # Participants for this day
    participants: List[ParticipantWithPreferences]
    
    # Daily toilet preferences summary
    toilet_preferences: Dict[str, int] = {"indian": 0, "western": 0}

    class Config:
        from_attributes = True


class EventDashboardResponse(BaseModel):
    """Complete dashboard response for an event"""
    event_id: str
    event_name: Optional[str] = None
    event_start_date: Optional[date] = None
    event_end_date: Optional[date] = None
    total_registrations: int
    total_participants: int
    confirmed_participants: int
    waiting_participants: int
    
    # Date-wise daily schedule
    daily_schedule: List[DailyScheduleItem]
    
    # Summary statistics
    summary: dict = Field(..., description="Summary statistics for the event")

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    """Summary statistics for dashboard"""
    total_groups: int
    individual_registrations: int
    group_registrations: int
    public_transport: int
    private_transport: int
    groups_with_empty_seats: int
    total_empty_seats: int
    gender_distribution: dict
    age_groups: dict
    city_distribution: dict
    toilet_preferences: dict
    daily_toilet_preferences: Dict[str, Dict[str, int]]

    class Config:
        from_attributes = True
