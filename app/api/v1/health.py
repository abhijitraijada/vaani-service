from fastapi import APIRouter, Depends
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from typing import List, Dict

from app.utils.database import get_db, engine

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check():
    """
    Check if the application is running
    """
    return {"status": "healthy", "message": "Application is running"}

@router.get("/database/tables", response_model=Dict[str, List[str]])
def get_database_tables(db: Session = Depends(get_db)):
    """
    Get list of all tables in the database
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}
