from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base


class VehicleSharing(Base):
    __tablename__ = "vehicle_sharing"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    vehicle_owner_member_id = Column(
        String(36),
        ForeignKey('registration_members.id'),
        nullable=True,
        comment='References registration_members.id'
    )
    co_traveler_member_id = Column(
        String(36),
        ForeignKey('registration_members.id'),
        nullable=True,
        comment='References registration_members.id'
    )
    sharing_notes = Column(Text, nullable=True, comment='Sharing arrangement notes')
    created_at = Column(
        DateTime,
        nullable=True,
        server_default=expression.text('CURRENT_TIMESTAMP'),
        comment='Creation timestamp'
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        server_default=expression.text('CURRENT_TIMESTAMP'),
        server_onupdate=expression.text('CURRENT_TIMESTAMP'),
        comment='Last update timestamp'
    )

    # Relationships
    vehicle_owner = relationship(
        "RegistrationMember",
        foreign_keys=[vehicle_owner_member_id],
        back_populates="owned_vehicle_shares"
    )
    co_traveler = relationship(
        "RegistrationMember",
        foreign_keys=[co_traveler_member_id],
        back_populates="co_traveler_shares"
    )
