from contextlib import asynccontextmanager
import os

from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

from .auth.auth import get_hashed_password
from .config.config import settings
from .models.users import User
from .routers.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup MongoDB Atlas com TLS
    app.state.client = AsyncIOMotorClient(
        settings.MONGO_HOST,
        tls=True,
        tlsCAFile=certifi.where()
    )
    await init_beanie(
        database=app.state.client[settings.MONGO_DB],
        document_models=[User],
    )

    # Criação do superusuário se não existir
    user = await User.find_one({"email": settings.FIRST_SUPERUSER})
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_hashed_password(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
        )
        await user.create()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Middleware CORS - flexível
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # já cobre tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(api_router, prefix=settings.API_V1_STR)


# --- Uvicorn entrypoint para Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render define PORT
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
