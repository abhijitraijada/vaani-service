from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.models import Event, EventDay
from app.schemas.event import EventCreate, EventResponse, EventListResponse
from app.utils.database import get_db
from app.utils.logger import logger

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/", response_model=EventListResponse)
async def list_events(db: Session = Depends(get_db)):
    """
    Get all events with their event days
    """
    events = db.query(Event).all()
    return {"events": events}


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """
    Create a new event with event days
    """
    try:
        # Create event with UUID
        event = Event(
            id=str(uuid.uuid4()),
            event_name=event_data.event_name,
            start_date=event_data.start_date,
            end_date=event_data.end_date,
            location_name=event_data.location_name,
            location_map_link=event_data.location_map_link,
            description=event_data.description,
            ngo=event_data.ngo,
            is_active=event_data.is_active,
            allowed_registration=event_data.allowed_registration,
            registration_start_date=event_data.registration_start_date
        )
        db.add(event)
        db.flush()  # Get the event ID without committing

        # Create event days with UUIDs
        event_days = [
            EventDay(
                id=str(uuid.uuid4()),
                event_id=event.id,
                event_date=day.event_date,
                breakfast_provided=day.breakfast_provided,
                lunch_provided=day.lunch_provided,
                dinner_provided=day.dinner_provided,
                location_name=day.location_name,
                daily_notes=day.daily_notes
            )
            for day in event_data.event_days
        ]
        db.bulk_save_objects(event_days)
        db.commit()
        db.refresh(event)

        return event

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating event"
        )
