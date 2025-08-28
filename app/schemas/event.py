from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EventDayBase(BaseModel):
    event_date: date
    breakfast_provided: bool = False
    lunch_provided: bool = False
    dinner_provided: bool = False
    location_name: Optional[str] = None
    daily_notes: Optional[str] = None


class EventDayCreate(EventDayBase):
    pass


class EventDayResponse(EventDayBase):
    id: str
    event_id: str

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    event_name: str
    start_date: date
    end_date: date
    location_name: str
    location_map_link: Optional[str] = None
    description: Optional[str] = None
    ngo: Optional[str] = None
    is_active: bool = True
    allowed_registration: Optional[int] = None
    registration_start_date: Optional[date] = None


class EventCreate(EventBase):
    event_days: List[EventDayCreate]


class EventResponse(EventBase):
    id: str
    event_days: List[EventDayResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    events: List[EventResponse]
