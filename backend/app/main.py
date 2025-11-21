from contextlib import asynccontextmanager
import certifi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.seeds.populate_item_references import populate_initial_data

# Configurações
from app.config.config import settings

# Models
from app.models.users import User
from app.models.company import Company
from app.models.rating import Rating
from app.models.discard import Discard
from app.models.environmental_report import EnvironmentalReport
from app.models.item_reference import ItemReference

# Routers
from app.routers.api import api_router

# Seeds e serviços
from app.seeds import admin_setup
from app.auth.auth import get_hashed_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup MongoDB
    app.state.client = AsyncIOMotorClient(
        settings.MONGO_HOST,
        tls=True,
        tlsCAFile=certifi.where()
    )
    
    # Inicializar Beanie com todos os models
    await init_beanie(
        database=app.state.client[settings.MONGO_DB], 
        document_models=[
            User, 
            Company, 
            Discard, 
            Rating, 
            EnvironmentalReport,
            ItemReference
        ]
    )
    
    # Criar admin se não existir
    admin_service = admin_setup.AdminSetupService()
    await admin_service.create_admin_if_not_exists()

    yield
    
    print("🛑 Parando aplicação...")
    app.state.client.close()

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

# Inclui rotas principais da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# -----------------------------
# Rodar localmente ou no Render
# -----------------------------
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
