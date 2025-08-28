from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.database import Base


class Organiser(Base):
    __tablename__ = "organisers"

    id = Column(String(36), primary_key=True)
    event_id = Column(String(36), ForeignKey('event.id'), nullable=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone_no = Column(BigInteger, nullable=True)

    # Relationship
    event = relationship("Event", back_populates="organisers")
