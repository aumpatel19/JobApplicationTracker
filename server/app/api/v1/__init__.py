from fastapi import APIRouter
from .auth import router as auth_router
from .applications import router as applications_router
from .contacts import router as contacts_router
from .notes import router as notes_router
from .timeline import router as timeline_router
from .dashboard import router as dashboard_router
from .csv import router as csv_router
from .users import router as users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(applications_router, prefix="/applications", tags=["applications"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_router.include_router(notes_router, tags=["notes"])
api_router.include_router(timeline_router, tags=["timeline"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(csv_router, prefix="/csv", tags=["csv"])
api_router.include_router(users_router, tags=["users"])
