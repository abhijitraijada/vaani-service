from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.host_assignment import (
    HostAssignmentCreate, HostAssignmentUpdate, HostAssignmentResponse,
    HostAssignmentFilterParams, HostAssignmentListResponse, HostAssignmentDeleteResponse,
    BulkHostAssignmentCreate, BulkHostAssignmentResponse
)
from app.services.host_assignment import HostAssignmentService

router = APIRouter(prefix="/host-assignments", tags=["Host Assignments"])


@router.post("/", response_model=HostAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_host_assignment(
    assignment_data: HostAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create a new host assignment (Requires Authentication).
    
    This endpoint creates a new assignment of a registration member to a host 
    for a specific event day. Each member can only have one assignment per event day.
    
    Args:
        assignment_data: Assignment creation data including host_id, registration_member_id, 
                        event_day_id, and optional assignment_notes
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostAssignmentResponse: Created assignment information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If host, member, or event day not found
        400: If member already has assignment for this event day
        500: If internal server error occurs
    """
    return HostAssignmentService.create_assignment(db, assignment_data, current_user.id)


@router.post("/bulk", response_model=BulkHostAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_bulk_host_assignments(
    bulk_data: BulkHostAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Create multiple host assignments in one request (Requires Authentication).
    
    This endpoint creates multiple assignments of registration members to a host 
    for a specific event day in a single API call. This is more efficient than 
    creating individual assignments.
    
    Args:
        bulk_data: Bulk assignment data including host_id, list of registration_member_ids, 
                  event_day_id, and optional assignment_notes (applied to all assignments)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        BulkHostAssignmentResponse: Results including successful/failed counts and error messages
        
    Raises:
        401: If authentication token is invalid or missing
        404: If host, event day, or any registration member not found
        400: If host capacity exceeded or validation fails
        500: If internal server error occurs
    """
    return HostAssignmentService.create_bulk_assignments(db, bulk_data, current_user.id)


@router.get("/", response_model=HostAssignmentListResponse, status_code=status.HTTP_200_OK)
async def get_host_assignments(
    host_id: str = None,
    registration_member_id: str = None,
    event_day_id: str = None,
    assigned_by: str = None,
    has_notes: bool = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get host assignments with filters and pagination (Requires Authentication).
    
    This endpoint retrieves host assignments with various filtering options 
    and pagination support. All filter parameters are optional and can be combined.
    
    Args:
        host_id: Filter by host ID
        registration_member_id: Filter by registration member ID
        event_day_id: Filter by event day ID
        assigned_by: Filter by who made the assignment
        has_notes: Filter assignments with/without notes
        page: Page number (default: 1)
        page_size: Number of assignments per page (default: 10, max: 100)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostAssignmentListResponse: Paginated list of assignments with metadata
        
    Raises:
        401: If authentication token is invalid or missing
        400: If invalid filter values provided
        500: If internal server error occurs
    """
    # Validate page_size
    if page_size > 5000:
        page_size = 5000
    if page_size < 1:
        page_size = 10
    if page < 1:
        page = 1
    
    # Create filter parameters
    filters = HostAssignmentFilterParams(
        host_id=host_id,
        registration_member_id=registration_member_id,
        event_day_id=event_day_id,
        assigned_by=assigned_by,
        has_notes=has_notes
    )
    
    return HostAssignmentService.get_assignments_with_filters(db, filters, page, page_size)


@router.get("/{assignment_id}", response_model=HostAssignmentResponse, status_code=status.HTTP_200_OK)
async def get_host_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get a specific host assignment by ID (Requires Authentication).
    
    This endpoint retrieves a single host assignment record by its ID.
    
    Args:
        assignment_id: The ID of the assignment to retrieve
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostAssignmentResponse: Assignment information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If assignment is not found
        500: If internal server error occurs
    """
    assignment = HostAssignmentService.get_assignment_by_id(db, assignment_id)
    return HostAssignmentResponse.model_validate(assignment)


@router.put("/{assignment_id}", response_model=HostAssignmentResponse, status_code=status.HTTP_200_OK)
async def update_host_assignment(
    assignment_id: str,
    update_data: HostAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Update host assignment information (Requires Authentication).
    
    This endpoint allows updating assignment notes. The core assignment 
    (host, member, event day) cannot be changed after creation.
    
    Args:
        assignment_id: The ID of the assignment to update
        update_data: Assignment information to update (assignment_notes)
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostAssignmentResponse: Updated assignment information
        
    Raises:
        401: If authentication token is invalid or missing
        404: If assignment is not found
        500: If internal server error occurs
    """
    return HostAssignmentService.update_assignment(db, assignment_id, update_data)


@router.delete("/{assignment_id}", response_model=HostAssignmentDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_host_assignment(
    assignment_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Delete a host assignment (Requires Authentication).
    
    This endpoint deletes a host assignment record.
    
    Args:
        assignment_id: The ID of the assignment to delete
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        HostAssignmentDeleteResponse: Success message and deleted assignment ID
        
    Raises:
        401: If authentication token is invalid or missing
        404: If assignment is not found
        500: If internal server error occurs
    """
    return HostAssignmentService.delete_assignment(db, assignment_id)
