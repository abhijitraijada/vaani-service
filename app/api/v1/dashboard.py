from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.utils.auth import get_current_active_user
from app.schemas.user import UserResponse
from app.schemas.dashboard import EventDashboardResponse
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/event/{event_id}", response_model=EventDashboardResponse)
async def get_event_dashboard(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get comprehensive dashboard data for an event (Requires Authentication).
    
    This endpoint provides organizers and admins with detailed participant data
    for a specific event, including:
    - Date-wise daily schedule with participant preferences
    - All registration groups and their members
    - Summary statistics and analytics
    - Participant demographics and distribution
    
    Args:
        event_id: ID of the event to get dashboard data for
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        EventDashboardResponse: Complete dashboard data for the event
        
    Raises:
        401: If authentication token is invalid or missing
        404: If event is not found
        500: If internal server error occurs
    """
    return DashboardService.get_event_dashboard(db, event_id)
