import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.host_assignment import HostAssignment
from app.models.host import Host
from app.models.registration_member import RegistrationMember
from app.models.event_day import EventDay
from app.schemas.host_assignment import (
    HostAssignmentCreate, HostAssignmentUpdate, HostAssignmentResponse, 
    HostAssignmentFilterParams, HostAssignmentListResponse, HostAssignmentDeleteResponse
)


class HostAssignmentService:
    """Service class for host assignment-related operations"""
    
    @staticmethod
    def create_assignment(db: Session, assignment_data: HostAssignmentCreate, assigned_by: str) -> HostAssignmentResponse:
        """Create a new host assignment"""
        try:
            # Validate that host exists
            host = db.query(Host).filter(Host.id == assignment_data.host_id).first()
            if not host:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Host not found"
                )
            
            # Validate that registration member exists
            member = db.query(RegistrationMember).filter(RegistrationMember.id == assignment_data.registration_member_id).first()
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration member not found"
                )
            
            # Validate that event day exists
            event_day = db.query(EventDay).filter(EventDay.id == assignment_data.event_day_id).first()
            if not event_day:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event day not found"
                )
            
            # Check if assignment already exists for this member on this event day
            existing_assignment = db.query(HostAssignment).filter(
                HostAssignment.registration_member_id == assignment_data.registration_member_id,
                HostAssignment.event_day_id == assignment_data.event_day_id
            ).first()
            
            if existing_assignment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member already has an assignment for this event day"
                )
            
            # Create new assignment
            db_assignment = HostAssignment(
                id=str(uuid.uuid4()),
                host_id=assignment_data.host_id,
                registration_member_id=assignment_data.registration_member_id,
                event_day_id=assignment_data.event_day_id,
                assignment_notes=assignment_data.assignment_notes,
                assigned_by=assigned_by
            )
            
            db.add(db_assignment)
            db.commit()
            db.refresh(db_assignment)
            
            return HostAssignmentResponse.model_validate(db_assignment)
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create assignment"
            )
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    @staticmethod
    def get_assignment_by_id(db: Session, assignment_id: str) -> HostAssignment:
        """Get assignment by ID"""
        assignment = db.query(HostAssignment).filter(HostAssignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        return assignment
    
    @staticmethod
    def get_assignments_with_filters(
        db: Session, 
        filters: HostAssignmentFilterParams,
        page: int = 1,
        page_size: int = 10
    ) -> HostAssignmentListResponse:
        """Get assignments with filters and pagination"""
        try:
            # Start with base query
            query = db.query(HostAssignment)
            
            # Apply filters
            if filters.host_id:
                query = query.filter(HostAssignment.host_id == filters.host_id)
            
            if filters.registration_member_id:
                query = query.filter(HostAssignment.registration_member_id == filters.registration_member_id)
            
            if filters.event_day_id:
                query = query.filter(HostAssignment.event_day_id == filters.event_day_id)
            
            if filters.assigned_by:
                query = query.filter(HostAssignment.assigned_by == filters.assigned_by)
            
            if filters.has_notes is not None:
                if filters.has_notes:
                    query = query.filter(HostAssignment.assignment_notes.isnot(None))
                    query = query.filter(HostAssignment.assignment_notes != "")
                else:
                    query = query.filter(
                        (HostAssignment.assignment_notes.is_(None)) | 
                        (HostAssignment.assignment_notes == "")
                    )
            
            # Get total count
            total_count = query.count()
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Apply pagination and get results
            assignments = query.offset(offset).limit(page_size).all()
            
            # Convert to response objects
            assignment_responses = [HostAssignmentResponse.model_validate(assignment) for assignment in assignments]
            
            return HostAssignmentListResponse(
                assignments=assignment_responses,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get assignments with filters: {str(e)}"
            )
    
    @staticmethod
    def update_assignment(db: Session, assignment_id: str, update_data: HostAssignmentUpdate) -> HostAssignmentResponse:
        """Update assignment information"""
        try:
            # Get assignment from database
            assignment = HostAssignmentService.get_assignment_by_id(db, assignment_id)
            
            # Update fields if provided
            if update_data.assignment_notes is not None:
                assignment.assignment_notes = update_data.assignment_notes
            
            assignment.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(assignment)
            
            return HostAssignmentResponse.model_validate(assignment)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update assignment: {str(e)}"
            )
    
    @staticmethod
    def delete_assignment(db: Session, assignment_id: str) -> HostAssignmentDeleteResponse:
        """Delete an assignment"""
        try:
            # Get assignment from database
            assignment = HostAssignmentService.get_assignment_by_id(db, assignment_id)
            
            # Delete assignment
            db.delete(assignment)
            db.commit()
            
            return HostAssignmentDeleteResponse(
                message="Assignment deleted successfully",
                deleted_assignment_id=assignment_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete assignment: {str(e)}"
            )
