from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base
from app.schemas.enums import ToiletFacilities, GenderPreference


class Host(Base):
    __tablename__ = "hosts"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    event_id = Column(String(36), ForeignKey('event.id'), nullable=True)
    event_days_id = Column(String(36), ForeignKey('event_days.id'), nullable=True, comment='Event day this host belongs to')
    name = Column(String(255), nullable=True)
    phone_no = Column(BigInteger, nullable=True)
    place_name = Column(String(255), nullable=True, comment='Location/place name')
    max_participants = Column(Integer, nullable=True, comment='Maximum participants capacity')
    toilet_facilities = Column(
        SQLAlchemyEnum(ToiletFacilities, name='toilet_facilities_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment='Toilet facilities'
    )
    gender_preference = Column(
        SQLAlchemyEnum(GenderPreference, name='gender_preference_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment='Gender preference'
    )
    facilities_description = Column(Text, nullable=True, comment='Additional facilities')
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
    event = relationship("Event", back_populates="hosts")
    event_day = relationship("EventDay", back_populates="hosts")
    assignments = relationship("HostAssignment", back_populates="host")