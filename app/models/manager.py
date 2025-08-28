from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
from app.utils.database import Base


class Manager(Base):
    __tablename__ = "manager"

    id = Column(String(36), primary_key=True, comment='Primary Key')
    event_id = Column(String(36), ForeignKey('event.id'), nullable=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True, comment='References users.id')
    permissions = Column(JSON, nullable=True, comment='Manager specific permissions')
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
    event = relationship("Event", back_populates="managers")
    user = relationship("User", back_populates="managed_events")
