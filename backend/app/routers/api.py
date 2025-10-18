from fastapi import APIRouter

from . import login, users
from . import company_auth, company
from .  import password_reset
from . import object_recognition

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(company_auth.router, prefix="/company/login", tags=["company auth"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(password_reset.router, prefix="/company/resetPassword", tags=["company password reset"])
api_router.include_router(object_recognition.router, prefix="/object_recognition", tags=["Computer Vision Model"])

@api_router.get("/")
async def root():
    return {"message": "Backend API for FARM-docker operational !"}
