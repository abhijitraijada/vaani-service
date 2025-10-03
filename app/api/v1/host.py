from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.host import (
    HostCreate, HostUpdate, HostResponse, HostCSVUpload, HostDeleteResponse,
    HostFilterParams, HostListResponse
)
from app.services.host import HostService

router = APIRouter(prefix="/hosts", tags=["Hosts"])


@router.post("/", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
async def create_host(
    host_data: HostCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new host (Requires Authentication).
    
    This endpoint creates a new host record for an event with the following characteristics:
    - Host information including name, phone, location, and capacity
    - Toilet facilities and gender preferences
    - Maximum participants capacity
    - Optional facilities description
    - Phone number must be unique within the same event
    - Requires valid JWT token in Authorization header
    
    Args:
        host_data: Host creation data including event_id, name, phone_no, place_name, 
                  max_participants, toilet_facilities, gender_preference, and optional facilities_description
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostResponse: Created host information
        
    Raises:
        401: If authentication token is invalid or missing
        400: If phone number already exists for this event or validation fails
        500: If internal server error occurs
    """
    return HostService.create_host(db, host_data)


@router.get("/event/{event_id}", response_model=HostListResponse, status_code=status.HTTP_200_OK)
async def get_hosts_by_event(
    event_id: str,
    name: str = None,
    phone_no: int = None,
    place_name: str = None,
    min_capacity: int = None,
    max_capacity: int = None,
    toilet_facilities: str = None,
    gender_preference: str = None,
    has_facilities_description: bool = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get hosts for a specific event with filters and pagination (Requires Authentication).
    
    This endpoint retrieves hosts for a specific event with various filtering options 
    and pagination support. All filter parameters are optional and can be combined.
    
    Args:
        event_id: The ID of the event to get hosts for (required)
        name: Filter by host name (partial match, case-insensitive)
        phone_no: Filter by exact phone number
        place_name: Filter by place name (partial match, case-insensitive)
        min_capacity: Minimum capacity filter (inclusive)
        max_capacity: Maximum capacity filter (inclusive)
        toilet_facilities: Filter by toilet facilities (indian, western, both)
        gender_preference: Filter by gender preference (male, female, both)
        has_facilities_description: Filter hosts with/without facilities description
        page: Page number (default: 1)
        page_size: Number of hosts per page (default: 10, max: 100)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostListResponse: Paginated list of hosts with metadata
        
    Raises:
        401: If authentication token is invalid or missing
        400: If invalid filter values provided
        500: If internal server error occurs
    """
    # Validate page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 10
    if page < 1:
        page = 1
    
    # Create filter parameters (event_id is always required)
    filters = HostFilterParams(
        event_id=event_id,
        name=name,
        phone_no=phone_no,
        place_name=place_name,
        min_capacity=min_capacity,
        max_capacity=max_capacity,
        toilet_facilities=toilet_facilities,
        gender_preference=gender_preference,
        has_facilities_description=has_facilities_description
    )
    
    return HostService.get_hosts_with_filters(db, filters, page, page_size)


@router.get("/{host_id}", response_model=HostResponse, status_code=status.HTTP_200_OK)
async def get_host(
    host_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific host by ID (Requires Authentication).
    
    This endpoint retrieves a single host record by its ID.
    
    Args:
        host_id: The ID of the host to retrieve
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostResponse: Host information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If host is not found
        500: If internal server error occurs
    """
    host = HostService.get_host_by_id(db, host_id)
    return HostResponse.model_validate(host)


@router.put("/{host_id}", response_model=HostResponse, status_code=status.HTTP_200_OK)
async def update_host(
    host_id: str,
    update_data: HostUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update host information (Requires Authentication).
    
    This endpoint allows updating host information. All fields are optional.
    If phone number is being updated, it must remain unique within the same event.
    
    Args:
        host_id: The ID of the host to update
        update_data: Host information to update (all fields optional)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostResponse: Updated host information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If host is not found
        400: If phone number already exists for this event
        500: If internal server error occurs
    """
    return HostService.update_host(db, host_id, update_data)


@router.delete("/{host_id}", response_model=HostDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_host(
    host_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a host (Requires Authentication).
    
    This endpoint deletes a host record. The host cannot be deleted if it has 
    existing assignments. All assignments must be removed first.
    
    Args:
        host_id: The ID of the host to delete
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostDeleteResponse: Success message and deleted host ID
        
    Raises:
        401: If authentication token is invalid or missing
        404: If host is not found
        400: If host has existing assignments
        500: If internal server error occurs
    """
    return HostService.delete_host(db, host_id)


@router.post("/upload-csv/{event_id}", response_model=HostCSVUpload, status_code=status.HTTP_200_OK)
async def upload_hosts_csv(
    event_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Upload hosts from CSV file (Requires Authentication).
    
    This endpoint allows bulk creation of hosts by uploading a CSV file.
    The CSV file must contain the required columns in the correct order.
    
    CSV Format Requirements:
    - name: Host's name (required)
    - phone_no: Host's phone number (required, numeric)
    - place_name: Location/place name (required)
    - max_participants: Maximum participants capacity (required, positive integer)
    - toilet_facilities: Available toilet facilities (required, one of: indian, western, both - case insensitive)
    - gender_preference: Gender preference for participants (required, one of: male, female, both - case insensitive)
    - facilities_description: Additional facilities description (optional)
    
    Args:
        event_id: The ID of the event to add hosts to
        file: CSV file containing host data
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostCSVUpload: Upload results including success/failure counts and error messages
        
    Raises:
        401: If authentication token is invalid or missing
        400: If CSV file is invalid or empty
        500: If internal server error occurs
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    return HostService.upload_hosts_csv(db, event_id, file)
