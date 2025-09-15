import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.vehicle_sharing import VehicleSharing
from app.models.registration_member import RegistrationMember
from app.schemas.vehicle_sharing import (
    VehicleSharingCreate, VehicleSharingUpdate, VehicleSharingResponse, 
    VehicleSharingFilterParams, VehicleSharingListResponse, VehicleSharingDeleteResponse
)


class VehicleSharingService:
    """Service class for vehicle sharing-related operations"""
    
    @staticmethod
    def create_arrangement(db: Session, arrangement_data: VehicleSharingCreate) -> VehicleSharingResponse:
        """Create a new vehicle sharing arrangement"""
        try:
            # Validate that vehicle owner exists
            vehicle_owner = db.query(RegistrationMember).filter(
                RegistrationMember.id == arrangement_data.vehicle_owner_member_id
            ).first()
            if not vehicle_owner:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Vehicle owner not found"
                )
            
            # Validate that co-traveler exists
            co_traveler = db.query(RegistrationMember).filter(
                RegistrationMember.id == arrangement_data.co_traveler_member_id
            ).first()
            if not co_traveler:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Co-traveler not found"
                )
            
            # Check if arrangement already exists between these two members
            existing_arrangement = db.query(VehicleSharing).filter(
                VehicleSharing.vehicle_owner_member_id == arrangement_data.vehicle_owner_member_id,
                VehicleSharing.co_traveler_member_id == arrangement_data.co_traveler_member_id
            ).first()
            
            if existing_arrangement:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle sharing arrangement already exists between these members"
                )
            
            # Check reverse arrangement (co-traveler as owner, owner as co-traveler)
            reverse_arrangement = db.query(VehicleSharing).filter(
                VehicleSharing.vehicle_owner_member_id == arrangement_data.co_traveler_member_id,
                VehicleSharing.co_traveler_member_id == arrangement_data.vehicle_owner_member_id
            ).first()
            
            if reverse_arrangement:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reverse vehicle sharing arrangement already exists"
                )
            
            # Create new arrangement
            db_arrangement = VehicleSharing(
                id=str(uuid.uuid4()),
                vehicle_owner_member_id=arrangement_data.vehicle_owner_member_id,
                co_traveler_member_id=arrangement_data.co_traveler_member_id,
                sharing_notes=arrangement_data.sharing_notes
            )
            
            db.add(db_arrangement)
            db.commit()
            db.refresh(db_arrangement)
            
            return VehicleSharingResponse.model_validate(db_arrangement)
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create vehicle sharing arrangement"
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
    def get_arrangement_by_id(db: Session, arrangement_id: str) -> VehicleSharing:
        """Get arrangement by ID"""
        arrangement = db.query(VehicleSharing).filter(VehicleSharing.id == arrangement_id).first()
        if not arrangement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle sharing arrangement not found"
            )
        return arrangement
    
    @staticmethod
    def get_arrangements_with_filters(
        db: Session, 
        filters: VehicleSharingFilterParams,
        page: int = 1,
        page_size: int = 10
    ) -> VehicleSharingListResponse:
        """Get arrangements with filters and pagination"""
        try:
            # Start with base query
            query = db.query(VehicleSharing)
            
            # Apply filters
            if filters.vehicle_owner_member_id:
                query = query.filter(VehicleSharing.vehicle_owner_member_id == filters.vehicle_owner_member_id)
            
            if filters.co_traveler_member_id:
                query = query.filter(VehicleSharing.co_traveler_member_id == filters.co_traveler_member_id)
            
            if filters.has_notes is not None:
                if filters.has_notes:
                    query = query.filter(VehicleSharing.sharing_notes.isnot(None))
                    query = query.filter(VehicleSharing.sharing_notes != "")
                else:
                    query = query.filter(
                        (VehicleSharing.sharing_notes.is_(None)) | 
                        (VehicleSharing.sharing_notes == "")
                    )
            
            # Get total count
            total_count = query.count()
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Apply pagination and get results
            arrangements = query.offset(offset).limit(page_size).all()
            
            # Convert to response objects
            arrangement_responses = [VehicleSharingResponse.model_validate(arrangement) for arrangement in arrangements]
            
            return VehicleSharingListResponse(
                arrangements=arrangement_responses,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get arrangements with filters: {str(e)}"
            )
    
    @staticmethod
    def update_arrangement(db: Session, arrangement_id: str, update_data: VehicleSharingUpdate) -> VehicleSharingResponse:
        """Update arrangement information"""
        try:
            # Get arrangement from database
            arrangement = VehicleSharingService.get_arrangement_by_id(db, arrangement_id)
            
            # Update fields if provided
            if update_data.sharing_notes is not None:
                arrangement.sharing_notes = update_data.sharing_notes
            
            arrangement.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(arrangement)
            
            return VehicleSharingResponse.model_validate(arrangement)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update arrangement: {str(e)}"
            )
    
    @staticmethod
    def delete_arrangement(db: Session, arrangement_id: str) -> VehicleSharingDeleteResponse:
        """Delete an arrangement"""
        try:
            # Get arrangement from database
            arrangement = VehicleSharingService.get_arrangement_by_id(db, arrangement_id)
            
            # Delete arrangement
            db.delete(arrangement)
            db.commit()
            
            return VehicleSharingDeleteResponse(
                message="Vehicle sharing arrangement deleted successfully",
                deleted_arrangement_id=arrangement_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete arrangement: {str(e)}"
            )
