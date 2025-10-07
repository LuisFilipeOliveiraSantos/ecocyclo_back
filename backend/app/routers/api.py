from fastapi import APIRouter

from . import login, users
from . import company_auth, company

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(company_auth.router, prefix="/company/login", tags=["company auth"])
api_router.include_router(company.router, prefix="/company", tags=["company"])

@api_router.get("/")
async def root():
    return {"message": "Backend API for FARM-docker operational !"}
