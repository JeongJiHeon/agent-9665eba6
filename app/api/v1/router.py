"""API v1 router"""

from fastapi import APIRouter
from app.api.v1 import auth, agent, events

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
