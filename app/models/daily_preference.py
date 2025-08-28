from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base
from app.schemas.enums import ToiletPreference


class DailyPreference(Base):
    __tablename__ = "daily_preferences"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    event_day_id = Column(
        String(36),
        ForeignKey('event_days.id'),
        nullable=True,
        comment='References event_days.id'
    )
    registration_id = Column(Integer, ForeignKey('registrations.id'), nullable=True)
    staying_with_yatra = Column(Boolean, nullable=True, comment='Staying with yatra flag')
    dinner_at_host = Column(Boolean, nullable=True, comment='Dinner at host place')
    breakfast_at_host = Column(Boolean, nullable=True, comment='Breakfast at host place')
    lunch_with_yatra = Column(Boolean, nullable=True, comment='Lunch with yatra group')
    physical_limitations = Column(Text, nullable=True, comment='Physical limitations description')
    toilet_preference = Column(
        SQLAlchemyEnum(ToiletPreference, name='toilet_preference_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment='Toilet preference'
    )
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
    event_day = relationship("EventDay", back_populates="daily_preferences")
    registration = relationship("Registration", back_populates="daily_preferences")
