from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base
from app.schemas.enums import RegistrationType, TransportationMode


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), ForeignKey('event.id'), nullable=True)
    registration_type = Column(
        String,
        nullable=True,
        comment='Registration type'
    )
    number_of_members = Column(Integer, nullable=True)
    transportation_mode = Column(
        String,
        nullable=True,
        comment='Transportation mode'
    )
    has_empty_seats = Column(Boolean, nullable=True)
    available_seats_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
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
    event = relationship("Event", back_populates="registrations")
    members = relationship("RegistrationMember", back_populates="registration")
    daily_preferences = relationship("DailyPreference", back_populates="registration")