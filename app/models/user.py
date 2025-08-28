from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base
from app.schemas.enums import UserType


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    phone_number = Column(String(255), nullable=True, unique=True, comment='Unique phone for login')
    password_hash = Column(String(255), nullable=True, comment='bcrypt hashed password')
    name = Column(String(255), nullable=True, comment='Full name')
    email = Column(String(255), nullable=True, comment='Email address')
    user_type = Column(
        SQLAlchemyEnum(UserType, name='user_type_enum', values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        comment='organiser, admin'
    )
    is_active = Column(Boolean, nullable=True, server_default=expression.true(), comment='Active status')
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
    managed_events = relationship("Manager", back_populates="user")
    assigned_host_assignments = relationship("HostAssignment", back_populates="assigned_by_user")
