from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base


class HostAssignment(Base):
    __tablename__ = "host_assignments"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    host_id = Column(String(36), ForeignKey('hosts.id'), nullable=True, comment='References hosts.id')
    registration_member_id = Column(
        String(36),
        ForeignKey('registration_members.id'),
        nullable=True,
        comment='References registration_members.id'
    )
    event_day_id = Column(
        String(36),
        ForeignKey('event_days.id'),
        nullable=True,
        comment='References event_days.id'
    )
    assignment_notes = Column(Text, nullable=True, comment='Assignment notes')
    assigned_by = Column(
        String(36),
        ForeignKey('users.id'),
        nullable=True,
        comment='References users.id (manager/admin)'
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
    host = relationship("Host", back_populates="assignments")
    registration_member = relationship("RegistrationMember", back_populates="host_assignments")
    event_day = relationship("EventDay", back_populates="host_assignments")
    assigned_by_user = relationship("User", back_populates="assigned_host_assignments")
