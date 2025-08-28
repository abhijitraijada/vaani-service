from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base
from app.schemas.enums import Gender, RegistrationStatus


class RegistrationMember(Base):
    __tablename__ = "registration_members"

    id = Column(String(36), primary_key=True)
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)
    phone_number = Column(String(255), nullable=True, comment='Unique phone for login')
    name = Column(String(255), nullable=True, comment='Full name')
    email = Column(String(255), nullable=True, comment='Email address')
    city = Column(String(255), nullable=True, comment='City of residence')
    age = Column(Integer, nullable=True, comment='Age in years')
    gender = Column(
        SQLAlchemyEnum(Gender, name='gender_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment='Gender'
    )
    language = Column(String(255), nullable=True, comment='Preferred language')
    floor_preference = Column(String(255), nullable=True, comment='Floor preference')
    special_requirements = Column(Text, nullable=True, comment='Special requirements')
    status = Column(  # Added status field here
        SQLAlchemyEnum(RegistrationStatus, name='registration_status_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        server_default='registered',
        comment='Registration status'
    )
    created_at = Column(
        DateTime,
        nullable=True,
        server_default=expression.text('CURRENT_TIMESTAMP'),
        comment='Registration timestamp'
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        server_default=expression.text('CURRENT_TIMESTAMP'),
        server_onupdate=expression.text('CURRENT_TIMESTAMP'),
        comment='Last update timestamp'
    )

    # Relationships
    registration = relationship("Registration", back_populates="members")
    host_assignments = relationship("HostAssignment", back_populates="registration_member")
    owned_vehicle_shares = relationship(
        "VehicleSharing",
        foreign_keys="[VehicleSharing.vehicle_owner_member_id]",
        back_populates="vehicle_owner"
    )
    co_traveler_shares = relationship(
        "VehicleSharing",
        foreign_keys="[VehicleSharing.co_traveler_member_id]",
        back_populates="co_traveler"
    )