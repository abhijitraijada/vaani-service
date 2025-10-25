import uuid
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.registration_member import RegistrationMember
from app.schemas.registration import (
    RegistrationMemberUpdate, RegistrationMemberStatusUpdate, RegistrationMemberResponse
)
from app.schemas.enums import RegistrationStatus as StatusEnum


class RegistrationMemberService:
    """Service class for registration member-related operations"""
    
    @staticmethod
    def get_member_by_id(db: Session, member_id: str) -> RegistrationMember:
        """Get registration member by ID"""
        member = db.query(RegistrationMember).filter(RegistrationMember.id == member_id).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration member not found"
            )
        return member
    
    @staticmethod
    def update_member(
        db: Session, 
        member_id: str, 
        update_data: RegistrationMemberUpdate
    ) -> RegistrationMemberResponse:
        """Update registration member information"""
        try:
            # Get member from database
            member = RegistrationMemberService.get_member_by_id(db, member_id)
            
            # Update fields if provided
            if update_data.name is not None:
                member.name = update_data.name
            
            if update_data.email is not None:
                member.email = update_data.email
            
            if update_data.city is not None:
                member.city = update_data.city
            
            if update_data.age is not None:
                member.age = update_data.age
            
            if update_data.language is not None:
                member.language = update_data.language
            
            if update_data.floor_preference is not None:
                member.floor_preference = update_data.floor_preference
            
            if update_data.special_requirements is not None:
                member.special_requirements = update_data.special_requirements
            
            if update_data.status is not None:
                member.status = update_data.status
            
            member.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(member)
            
            return RegistrationMemberResponse.model_validate(member)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update member: {str(e)}"
            )
    
    @staticmethod
    def update_member_status(
        db: Session, 
        member_id: str, 
        status_data: RegistrationMemberStatusUpdate
    ) -> RegistrationMemberResponse:
        """Update only the registration status of a member - Optimized for minimal DB calls"""
        try:
            # Most efficient approach: Single UPDATE query with row count check
            from sqlalchemy import update
            
            # Single UPDATE query
            update_stmt = update(RegistrationMember).where(
                RegistrationMember.id == member_id
            ).values(
                status=status_data.status,
                updated_at=datetime.utcnow()
            )
            
            result = db.execute(update_stmt)
            
            # Check if any rows were affected (member exists)
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration member not found"
                )
            
            # If status is changed to CANCELLED, delete all host assignments for this member
            if status_data.status == StatusEnum.CANCELLED:
                from app.models.host_assignment import HostAssignment
                # Delete all host assignments for this member across all event days
                db.query(HostAssignment).filter(
                    HostAssignment.registration_member_id == member_id
                ).delete(synchronize_session=False)
            
            db.commit()
            
            # Single SELECT query to get updated member
            member = db.query(RegistrationMember).filter(
                RegistrationMember.id == member_id
            ).first()
            
            return RegistrationMemberResponse.model_validate(member)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update member status: {str(e)}"
            )
    
    @staticmethod
    def get_members_by_registration(
        db: Session, 
        registration_id: int
    ) -> List[RegistrationMemberResponse]:
        """Get all members for a specific registration"""
        members = db.query(RegistrationMember).filter(
            RegistrationMember.registration_id == registration_id
        ).all()
        
        return [RegistrationMemberResponse.model_validate(member) for member in members]
    
    @staticmethod
    def get_members_by_status(
        db: Session, 
        status: StatusEnum,
        event_id: str = None
    ) -> List[RegistrationMemberResponse]:
        """Get all members with a specific status, optionally filtered by event"""
        query = db.query(RegistrationMember).filter(RegistrationMember.status == status)
        
        if event_id:
            # Join with registration to filter by event
            from app.models.registration import Registration
            query = query.join(Registration).filter(Registration.event_id == event_id)
        
        members = query.all()
        return [RegistrationMemberResponse.model_validate(member) for member in members]
