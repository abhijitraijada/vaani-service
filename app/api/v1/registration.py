from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
import uuid

from app.utils.database import get_db
from app.models.registration import Registration
from app.models.registration_member import RegistrationMember
from app.models.daily_preference import DailyPreference
from app.models.event import Event
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse
)
from app.schemas.enums import RegistrationType, RegistrationStatus

router = APIRouter(prefix="/registrations", tags=["Registrations"])


async def get_current_registration_count(db: Session, event_id: str) -> int:
    """
    Get the count of current registrations (registered or confirmed) for an event
    """
    return db.query(func.count(RegistrationMember.id))\
        .join(Registration, Registration.id == RegistrationMember.registration_id)\
        .filter(
            Registration.event_id == event_id,
            RegistrationMember.status.in_([RegistrationStatus.REGISTERED, RegistrationStatus.CONFIRMED])
        ).scalar()


@router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    registration_data: RegistrationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new registration with members and their daily preferences.
    
    Validates:
    - For individual registrations, only one member is allowed
    - Number of members matches the members array length
    - Each member gets a UUID
    - Each daily preference is linked to the registration
    - Members are set to 'waiting' status if event's allowed_registration limit is exceeded
    """
    try:
        # Validate registration type and members count
        if (registration_data.registration_type == RegistrationType.INDIVIDUAL 
            and registration_data.number_of_members != 1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Individual registration must have exactly one member"
            )
        
        if len(registration_data.members) != registration_data.number_of_members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of members must match the members array length"
            )

        # Get event and check if it exists
        event = db.query(Event).filter(Event.id == registration_data.event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Get current registration count
        current_count = await get_current_registration_count(db, registration_data.event_id)
        
        # Create registration
        db_registration = Registration(
            event_id=registration_data.event_id,
            registration_type=registration_data.registration_type,
            number_of_members=registration_data.number_of_members,
            transportation_mode=registration_data.transportation_mode,
            has_empty_seats=registration_data.has_empty_seats,
            available_seats_count=registration_data.available_seats_count,
            notes=registration_data.notes
        )
        db.add(db_registration)
        db.flush()  # Get the registration ID

        # Create members with appropriate status
        for i, member_data in enumerate(registration_data.members, start=1):
            # Determine member status based on registration limit
            if event.allowed_registration and current_count + i > event.allowed_registration:
                member_status = RegistrationStatus.WAITING
            else:
                member_status = RegistrationStatus.REGISTERED

            db_member = RegistrationMember(
                id=str(uuid.uuid4()),
                registration_id=db_registration.id,
                status=member_status,  # Override any provided status
                **{k: v for k, v in member_data.dict().items() if k != 'status'}  # Exclude status from dict
            )
            db.add(db_member)

        # Create daily preferences
        for pref_data in registration_data.daily_preferences:
            db_preference = DailyPreference(
                id=str(uuid.uuid4()),
                registration_id=db_registration.id,
                **pref_data.dict()
            )
            db.add(db_preference)

        db.commit()
        db.refresh(db_registration)
        
        # Reload with relationships for response
        registration_with_relations = db.query(Registration)\
            .options(joinedload(Registration.members), joinedload(Registration.daily_preferences))\
            .filter(Registration.id == db_registration.id).first()
        
        return registration_with_relations

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{registration_id}", response_model=RegistrationResponse)
async def get_registration(registration_id: int, db: Session = Depends(get_db)):
    """
    Get a registration by ID, including all members and daily preferences
    """
    registration = db.query(Registration)\
        .options(joinedload(Registration.members), joinedload(Registration.daily_preferences))\
        .filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration with id {registration_id} not found"
        )
    return registration


@router.get("/", response_model=List[RegistrationResponse])
async def list_registrations(
    event_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all registrations, optionally filtered by event_id.
    Supports pagination with skip and limit parameters.
    """
    query = db.query(Registration)
    if event_id:
        query = query.filter(Registration.event_id == event_id)
    
    registrations = query.offset(skip).limit(limit).all()
    return registrations