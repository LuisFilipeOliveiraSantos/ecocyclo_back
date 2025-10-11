from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

import certifi
from .auth.auth import get_hashed_password
from .config.config import settings
from .models.users import User
from .routers.api import api_router
from .models.company import Company
from .seeds import seed_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup MongoDB
    app.state.client = AsyncIOMotorClient(
        settings.MONGO_HOST,
    )
    await init_beanie(
        database=app.state.client[settings.MONGO_DB], 
        document_models=[User, Company]
        
    )
    # Seed initial admin company
    await seed_admin.create_first_admin()

    # user = await User.find_one({"email": settings.FIRST_SUPERUSER})
    # if not user:
    #     user = User(
    #         email=settings.FIRST_SUPERUSER,
    #         hashed_password=get_hashed_password(settings.FIRST_SUPERUSER_PASSWORD),
    #         is_superuser=True,
    #     )
    #     await user.create()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configura CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Inclui rotas
app.include_router(api_router, prefix=settings.API_V1_STR)



# -----------------------------
# Rodar localmente ou no Render
# -----------------------------
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # Render fornece a porta dinamicamente
    uvicorn.run(app, host="0.0.0.0", port=port)
