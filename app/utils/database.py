from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.utils.config import get_settings
from app.utils.logger import logger
settings = get_settings()

# Create database engine
engine = create_engine(settings.VAANI_DATABASE_URL, pool_pre_ping=True, pool_recycle=300, pool_size=5, max_overflow=2)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    logger.info("Getting database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.info("Closing database session")
        db.close()
