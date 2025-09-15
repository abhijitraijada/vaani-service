import uuid
import csv
import io
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, UploadFile

from app.models.host import Host
from app.schemas.host import (
    HostCreate, HostUpdate, HostResponse, HostCSVRow, 
    HostCSVUpload, HostDeleteResponse, HostFilterParams, HostListResponse
)
from app.schemas.enums import ToiletFacilities, GenderPreference


class HostService:
    """Service class for host-related operations"""
    
    @staticmethod
    def create_host(db: Session, host_data: HostCreate) -> HostResponse:
        """Create a new host"""
        try:
            # Check if phone number already exists for this event
            existing_host = db.query(Host).filter(
                Host.event_id == host_data.event_id,
                Host.phone_no == host_data.phone_no
            ).first()
            
            if existing_host:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered for this event"
                )
            
            # Create new host
            db_host = Host(
                id=str(uuid.uuid4()),
                event_id=host_data.event_id,
                name=host_data.name,
                phone_no=host_data.phone_no,
                place_name=host_data.place_name,
                max_participants=host_data.max_participants,
                toilet_facilities=host_data.toilet_facilities,
                gender_preference=host_data.gender_preference,
                facilities_description=host_data.facilities_description
            )
            
            db.add(db_host)
            db.commit()
            db.refresh(db_host)
            
            return HostResponse.model_validate(db_host)
            
        except IntegrityError as e:
            db.rollback()
            if "phone_no" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered for this event"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create host"
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
    def get_host_by_id(db: Session, host_id: str) -> Host:
        """Get host by ID"""
        host = db.query(Host).filter(Host.id == host_id).first()
        if not host:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Host not found"
            )
        return host
    
    
    @staticmethod
    def update_host(db: Session, host_id: str, update_data: HostUpdate) -> HostResponse:
        """Update host information"""
        try:
            # Get host from database
            host = HostService.get_host_by_id(db, host_id)
            
            # Check if phone number is being updated and if it conflicts
            if update_data.phone_no is not None and update_data.phone_no != host.phone_no:
                existing_host = db.query(Host).filter(
                    Host.event_id == host.event_id,
                    Host.phone_no == update_data.phone_no,
                    Host.id != host_id
                ).first()
                
                if existing_host:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already registered for this event"
                    )
            
            # Update fields if provided
            if update_data.name is not None:
                host.name = update_data.name
            
            if update_data.phone_no is not None:
                host.phone_no = update_data.phone_no
            
            if update_data.place_name is not None:
                host.place_name = update_data.place_name
            
            if update_data.max_participants is not None:
                host.max_participants = update_data.max_participants
            
            if update_data.toilet_facilities is not None:
                host.toilet_facilities = update_data.toilet_facilities
            
            if update_data.gender_preference is not None:
                host.gender_preference = update_data.gender_preference
            
            if update_data.facilities_description is not None:
                host.facilities_description = update_data.facilities_description
            
            host.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(host)
            
            return HostResponse.model_validate(host)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update host: {str(e)}"
            )
    
    @staticmethod
    def delete_host(db: Session, host_id: str) -> HostDeleteResponse:
        """Delete a host"""
        try:
            # Get host from database
            host = HostService.get_host_by_id(db, host_id)
            
            # Check if host has any assignments
            if host.assignments:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete host with existing assignments. Please remove assignments first."
                )
            
            # Delete host
            db.delete(host)
            db.commit()
            
            return HostDeleteResponse(
                message="Host deleted successfully",
                deleted_host_id=host_id
            )
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete host: {str(e)}"
            )
    
    @staticmethod
    def validate_csv_row(row_data: dict, row_number: int) -> Tuple[bool, str]:
        """Validate a single CSV row"""
        try:
            # Check required fields
            required_fields = ['name', 'phone_no', 'place_name', 'max_participants', 'toilet_facilities', 'gender_preference']
            for field in required_fields:
                if field not in row_data or not row_data[field]:
                    return False, f"Row {row_number}: Missing required field '{field}'"
            
            # Validate phone number
            try:
                phone_no = int(row_data['phone_no'])
                if phone_no <= 0:
                    return False, f"Row {row_number}: Phone number must be positive"
            except ValueError:
                return False, f"Row {row_number}: Invalid phone number format"
            
            # Validate max participants
            try:
                max_participants = int(row_data['max_participants'])
                if max_participants <= 0:
                    return False, f"Row {row_number}: Max participants must be positive"
            except ValueError:
                return False, f"Row {row_number}: Invalid max participants format"
            
            # Validate toilet facilities
            toilet_facilities = row_data['toilet_facilities'].lower().strip()
            if toilet_facilities not in [e.value for e in ToiletFacilities]:
                return False, f"Row {row_number}: Invalid toilet facilities value. Must be one of: {[e.value for e in ToiletFacilities]}"
            
            # Validate gender preference
            gender_preference = row_data['gender_preference'].lower().strip()
            if gender_preference not in [e.value for e in GenderPreference]:
                return False, f"Row {row_number}: Invalid gender preference value. Must be one of: {[e.value for e in GenderPreference]}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Row {row_number}: Validation error - {str(e)}"
    
    @staticmethod
    def parse_csv_content(csv_content: str) -> List[dict]:
        """Parse CSV content and return list of dictionaries"""
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        return list(csv_reader)
    
    @staticmethod
    def upload_hosts_csv(db: Session, event_id: str, csv_file: UploadFile) -> HostCSVUpload:
        """Upload and process hosts from CSV file"""
        try:
            # Read CSV content
            csv_content = csv_file.file.read().decode('utf-8')
            csv_file.file.seek(0)  # Reset file pointer
            
            # Parse CSV
            rows = HostService.parse_csv_content(csv_content)
            
            if not rows:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV file is empty or invalid"
                )
            
            total_rows = len(rows)
            successful_imports = 0
            failed_imports = 0
            errors = []
            
            # Process each row
            for i, row_data in enumerate(rows, 1):
                # Validate row
                is_valid, error_message = HostService.validate_csv_row(row_data, i)
                
                if not is_valid:
                    failed_imports += 1
                    errors.append(error_message)
                    continue
                
                # Create host data
                try:
                    host_data = HostCreate(
                        event_id=event_id,
                        name=row_data['name'].strip(),
                        phone_no=int(row_data['phone_no']),
                        place_name=row_data['place_name'].strip(),
                        max_participants=int(row_data['max_participants']),
                        toilet_facilities=ToiletFacilities(row_data['toilet_facilities'].lower().strip()),
                        gender_preference=GenderPreference(row_data['gender_preference'].lower().strip()),
                        facilities_description=row_data.get('facilities_description', '').strip() or None
                    )
                    
                    # Create host
                    HostService.create_host(db, host_data)
                    successful_imports += 1
                    
                except Exception as e:
                    failed_imports += 1
                    errors.append(f"Row {i}: Failed to create host - {str(e)}")
            
            return HostCSVUpload(
                total_rows=total_rows,
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                errors=errors
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process CSV file: {str(e)}"
            )
    
    @staticmethod
    def get_hosts_with_filters(
        db: Session, 
        filters: HostFilterParams,
        page: int = 1,
        page_size: int = 10
    ) -> HostListResponse:
        """Get hosts with filters and pagination"""
        try:
            # Start with base query
            query = db.query(Host)
            
            # Apply filters
            if filters.event_id:
                query = query.filter(Host.event_id == filters.event_id)
            
            if filters.name:
                query = query.filter(Host.name.ilike(f"%{filters.name}%"))
            
            if filters.phone_no:
                query = query.filter(Host.phone_no == filters.phone_no)
            
            if filters.place_name:
                query = query.filter(Host.place_name.ilike(f"%{filters.place_name}%"))
            
            if filters.min_capacity:
                query = query.filter(Host.max_participants >= filters.min_capacity)
            
            if filters.max_capacity:
                query = query.filter(Host.max_participants <= filters.max_capacity)
            
            if filters.toilet_facilities:
                query = query.filter(Host.toilet_facilities == filters.toilet_facilities)
            
            if filters.gender_preference:
                query = query.filter(Host.gender_preference == filters.gender_preference)
            
            if filters.has_facilities_description is not None:
                if filters.has_facilities_description:
                    query = query.filter(Host.facilities_description.isnot(None))
                    query = query.filter(Host.facilities_description != "")
                else:
                    query = query.filter(
                        (Host.facilities_description.is_(None)) | 
                        (Host.facilities_description == "")
                    )
            
            # Get total count
            total_count = query.count()
            
            # Calculate pagination
            total_pages = (total_count + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Apply pagination and get results
            hosts = query.offset(offset).limit(page_size).all()
            
            # Convert to response objects
            host_responses = [HostResponse.model_validate(host) for host in hosts]
            
            return HostListResponse(
                hosts=host_responses,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get hosts with filters: {str(e)}"
            )
