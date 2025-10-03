from datetime import date
from sqlalchemy import Column, String, Boolean, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base


class EventDay(Base):
    __tablename__ = "event_days"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    event_id = Column(String(36), ForeignKey('event.id'), nullable=True)
    event_date = Column(Date, nullable=True, comment='Specific date (Oct 31, Nov 1, 2, 3)')
    breakfast_provided = Column(Boolean, nullable=True, comment='Breakfast provided by yatra')
    lunch_provided = Column(Boolean, nullable=True, comment='Lunch provided by yatra')
    dinner_provided = Column(Boolean, nullable=True, comment='Dinner provided by yatra')
    location_name = Column(String(255), nullable=True, comment='Day specific location')
    daily_notes = Column(Text, nullable=True, comment='Day specific notes')
    created_at = Column(
        DateTime,
        nullable=True,
        server_default=expression.text('CURRENT_TIMESTAMP'),
        comment='Creation timestamp'
    )

    # Relationships
    event = relationship("Event", back_populates="event_days")
    hosts = relationship("Host", back_populates="event_day")
    host_assignments = relationship("HostAssignment", back_populates="event_day")
    daily_preferences = relationship("DailyPreference", back_populates="event_day")
