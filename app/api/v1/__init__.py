from fastapi import APIRouter
from .base import BaseRouter
from .health import router as health_router
from .event import router as event_router
from .registration import router as registration_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(event_router)
api_router.include_router(registration_router)

__all__ = ['api_router', 'BaseRouter']