from datetime import date, datetime
from sqlalchemy import Column, String, Date, Text, Boolean, Integer, DateTime
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base


class Event(Base):
    __tablename__ = "event"

    id = Column(String(36), primary_key=True)
    event_name = Column(String(255), nullable=True, comment='Name of the event')
    start_date = Column(Date, nullable=True, comment='Event start date')
    end_date = Column(Date, nullable=True, comment='Event end date')
    location_name = Column(String(255), nullable=True, comment='Village/location name')
    location_map_link = Column(String(255), nullable=True, comment='Google maps link')
    description = Column(Text, nullable=True, comment='Event description')
    ngo = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=True, server_default=expression.true(), comment='Active status')
    allowed_registration = Column(Integer, nullable=True)
    registration_start_date = Column(Date, nullable=True)
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
    organisers = relationship("Organiser", back_populates="event")
    managers = relationship("Manager", back_populates="event")
    hosts = relationship("Host", back_populates="event")
    event_days = relationship("EventDay", back_populates="event")
    registrations = relationship("Registration", back_populates="event")
