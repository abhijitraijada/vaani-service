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
from app.models.host_assignment import HostAssignment
from app.models.host import Host
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse,
    RegistrationMemberUpdate,
    RegistrationMemberStatusUpdate,
    RegistrationMemberResponse
)
from app.schemas.enums import RegistrationType, RegistrationStatus
from app.schemas.participant_search import ParticipantSearchResponse, HostAssignmentInfo
from app.services.registration_member import RegistrationMemberService
from app.utils.auth import get_current_active_user
from app.schemas.user import UserResponse

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


@router.get("/search/participant", response_model=ParticipantSearchResponse)
async def search_participant_by_phone(
    phone_number: str,
    db: Session = Depends(get_db)
):
    """
    Search for a participant by phone number and return comprehensive data.
    
    This endpoint performs a single optimized query to retrieve:
    1. Participant data and registration status
    2. All members in the group if it's a group registration
    3. Merged daily schedule combining event days with user preferences
    
    Returns 404 if no participant is found with the given phone number.
    """
    # Single optimized query with all necessary joins (host assignments included)
    registration = db.query(Registration)\
        .options(
            joinedload(Registration.members)
                .joinedload(RegistrationMember.host_assignments)
                .joinedload(HostAssignment.host),
            joinedload(Registration.members)
                .joinedload(RegistrationMember.host_assignments)
                .joinedload(HostAssignment.event_day),
            joinedload(Registration.daily_preferences).joinedload(DailyPreference.event_day)
        )\
        .join(RegistrationMember, Registration.id == RegistrationMember.registration_id)\
        .filter(RegistrationMember.phone_number == phone_number)\
        .first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No participant found with phone number: {phone_number}"
        )
    
    # Create merged daily schedule
    daily_schedule = []
    for preference in registration.daily_preferences:
        event_day = preference.event_day
        if event_day:
            schedule_item = {
                # Event Day Information
                "event_day_id": event_day.id,
                "event_date": event_day.event_date,
                "location_name": event_day.location_name,
                "breakfast_provided": event_day.breakfast_provided,
                "lunch_provided": event_day.lunch_provided,
                "dinner_provided": event_day.dinner_provided,
                "daily_notes": event_day.daily_notes,
                
                # User Preferences for this day
                "preference_id": preference.id,
                "staying_with_yatra": preference.staying_with_yatra,
                "dinner_at_host": preference.dinner_at_host,
                "breakfast_at_host": preference.breakfast_at_host,
                "lunch_with_yatra": preference.lunch_with_yatra,
                "physical_limitations": preference.physical_limitations,
                "toilet_preference": preference.toilet_preference,
                
                # Timestamps
                "created_at": preference.created_at,
                "updated_at": preference.updated_at
            }
            daily_schedule.append(schedule_item)
    
    # Build members list with host assignment details
    members_data = []
    for member in registration.members:
        # Build host assignments for this member
        host_assignments = []
        if member.status in [RegistrationStatus.REGISTERED, RegistrationStatus.CONFIRMED]:
            if hasattr(member, 'host_assignments') and member.host_assignments:
                for assignment in member.host_assignments:
                    if assignment.host:  # Check if host is loaded
                        host_assignments.append(HostAssignmentInfo(
                            event_day_id=assignment.event_day_id,
                            host_name=assignment.host.name,
                            host_phone=str(assignment.host.phone_no) if assignment.host.phone_no else None,
                            host_location=assignment.host.place_name
                        ))
        
        # Create member dict with host assignments
        member_dict = {
            "id": member.id,
            "registration_id": member.registration_id,
            "name": member.name,
            "phone_number": member.phone_number,
            "email": member.email,
            "city": member.city,
            "age": member.age,
            "gender": member.gender,
            "language": member.language,
            "floor_preference": member.floor_preference,
            "special_requirements": member.special_requirements,
            "status": member.status,
            "created_at": member.created_at,
            "updated_at": member.updated_at,
            "host_assignments": host_assignments
        }
        members_data.append(member_dict)
    
    # Create response with merged daily schedule
    response_data = {
        "registration_id": registration.id,
        "event_id": registration.event_id,
        "registration_type": registration.registration_type,
        "transportation_mode": registration.transportation_mode,
        "has_empty_seats": registration.has_empty_seats,
        "available_seats_count": registration.available_seats_count,
        "notes": registration.notes,
        "created_at": registration.created_at,
        "updated_at": registration.updated_at,
        "members": members_data,
        "daily_schedule": daily_schedule
    }
    
    return response_data


@router.put("/members/{member_id}", response_model=RegistrationMemberResponse, status_code=status.HTTP_200_OK)
async def update_registration_member(
    member_id: str,
    update_data: RegistrationMemberUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update registration member information (Requires Authentication).
    
    This endpoint allows updating various fields of a registration member including
    personal information and registration status.
    
    Args:
        member_id: The ID of the registration member to update
        update_data: Member information to update (all fields optional)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        RegistrationMemberResponse: Updated member information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If member is not found
        500: If internal server error occurs
    """
    return RegistrationMemberService.update_member(db, member_id, update_data)


@router.put("/members/{member_id}/status", response_model=RegistrationMemberResponse, status_code=status.HTTP_200_OK)
async def update_member_status(
    member_id: str,
    status_data: RegistrationMemberStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update registration member status only (Requires Authentication).
    
    This endpoint allows updating only the registration status of a member.
    Useful for confirming registrations, moving from waiting to confirmed, etc.
    
    Args:
        member_id: The ID of the registration member to update
        status_data: New status information
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        RegistrationMemberResponse: Updated member information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If member is not found
        500: If internal server error occurs
    """
    return RegistrationMemberService.update_member_status(db, member_id, status_data)


@router.get("/members/registration/{registration_id}", response_model=List[RegistrationMemberResponse], status_code=status.HTTP_200_OK)
async def get_registration_members(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get all members for a specific registration (Requires Authentication).
    
    This endpoint retrieves all registration members belonging to a specific registration.
    
    Args:
        registration_id: The ID of the registration to get members for
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        List[RegistrationMemberResponse]: List of members for the registration
        
    Raises:
        401: If authentication token is invalid or missing
        500: If internal server error occurs
    """
    return RegistrationMemberService.get_members_by_registration(db, registration_id)


@router.get("/members/status/{status}", response_model=List[RegistrationMemberResponse], status_code=status.HTTP_200_OK)
async def get_members_by_status(
    status: RegistrationStatus,
    event_id: str = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get all members with a specific status (Requires Authentication).
    
    This endpoint retrieves all registration members with a specific status,
    optionally filtered by event.
    
    Args:
        status: The registration status to filter by (registered, waiting, confirmed, cancelled)
        event_id: Optional event ID to filter members by event
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        List[RegistrationMemberResponse]: List of members with the specified status
        
    Raises:
        401: If authentication token is invalid or missing
        500: If internal server error occurs
    """
    return RegistrationMemberService.get_members_by_status(db, status, event_id)