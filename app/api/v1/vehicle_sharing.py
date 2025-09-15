from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.vehicle_sharing import (
    VehicleSharingCreate, VehicleSharingUpdate, VehicleSharingResponse,
    VehicleSharingFilterParams, VehicleSharingListResponse, VehicleSharingDeleteResponse
)
from app.services.vehicle_sharing import VehicleSharingService

router = APIRouter(prefix="/vehicle-sharing", tags=["Vehicle Sharing"])


@router.post("/", response_model=VehicleSharingResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle_sharing(
    arrangement_data: VehicleSharingCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new vehicle sharing arrangement (Requires Authentication).
    
    This endpoint creates a new vehicle sharing arrangement between two registration members.
    Each pair of members can only have one arrangement (prevents duplicate arrangements).
    
    Args:
        arrangement_data: Arrangement creation data including vehicle_owner_member_id, 
                         co_traveler_member_id, and optional sharing_notes
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        VehicleSharingResponse: Created arrangement information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If vehicle owner or co-traveler not found
        400: If arrangement already exists between these members
        500: If internal server error occurs
    """
    return VehicleSharingService.create_arrangement(db, arrangement_data)


@router.get("/", response_model=VehicleSharingListResponse, status_code=status.HTTP_200_OK)
async def get_vehicle_sharing_arrangements(
    vehicle_owner_member_id: str = None,
    co_traveler_member_id: str = None,
    has_notes: bool = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get vehicle sharing arrangements with filters and pagination (Requires Authentication).
    
    This endpoint retrieves vehicle sharing arrangements with various filtering options 
    and pagination support. All filter parameters are optional and can be combined.
    
    Args:
        vehicle_owner_member_id: Filter by vehicle owner member ID
        co_traveler_member_id: Filter by co-traveler member ID
        has_notes: Filter arrangements with/without notes
        page: Page number (default: 1)
        page_size: Number of arrangements per page (default: 10, max: 100)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        VehicleSharingListResponse: Paginated list of arrangements with metadata
        
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
    
    # Create filter parameters
    filters = VehicleSharingFilterParams(
        vehicle_owner_member_id=vehicle_owner_member_id,
        co_traveler_member_id=co_traveler_member_id,
        has_notes=has_notes
    )
    
    return VehicleSharingService.get_arrangements_with_filters(db, filters, page, page_size)


@router.get("/{arrangement_id}", response_model=VehicleSharingResponse, status_code=status.HTTP_200_OK)
async def get_vehicle_sharing_arrangement(
    arrangement_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific vehicle sharing arrangement by ID (Requires Authentication).
    
    This endpoint retrieves a single vehicle sharing arrangement record by its ID.
    
    Args:
        arrangement_id: The ID of the arrangement to retrieve
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        VehicleSharingResponse: Arrangement information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If arrangement is not found
        500: If internal server error occurs
    """
    arrangement = VehicleSharingService.get_arrangement_by_id(db, arrangement_id)
    return VehicleSharingResponse.model_validate(arrangement)


@router.put("/{arrangement_id}", response_model=VehicleSharingResponse, status_code=status.HTTP_200_OK)
async def update_vehicle_sharing_arrangement(
    arrangement_id: str,
    update_data: VehicleSharingUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update vehicle sharing arrangement information (Requires Authentication).
    
    This endpoint allows updating sharing notes. The core arrangement 
    (vehicle owner, co-traveler) cannot be changed after creation.
    
    Args:
        arrangement_id: The ID of the arrangement to update
        update_data: Arrangement information to update (sharing_notes)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        VehicleSharingResponse: Updated arrangement information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If arrangement is not found
        500: If internal server error occurs
    """
    return VehicleSharingService.update_arrangement(db, arrangement_id, update_data)


@router.delete("/{arrangement_id}", response_model=VehicleSharingDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_vehicle_sharing_arrangement(
    arrangement_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a vehicle sharing arrangement (Requires Authentication).
    
    This endpoint deletes a vehicle sharing arrangement record.
    
    Args:
        arrangement_id: The ID of the arrangement to delete
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        VehicleSharingDeleteResponse: Success message and deleted arrangement ID
        
    Raises:
        401: If authentication token is invalid or missing
        404: If arrangement is not found
        500: If internal server error occurs
    """
    return VehicleSharingService.delete_arrangement(db, arrangement_id)
