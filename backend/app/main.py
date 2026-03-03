from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.v1.router import router as api_router
from app.api.health import router as health_router

# Ensure upload directory exists before app initialization
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create first admin user if not exists
    from app.db.database import AsyncSessionLocal
    from app.repositories.user_repository import UserRepository
    from app.services.auth_service import AuthService

    async with AsyncSessionLocal() as db:
        service = AuthService(UserRepository(db))
        await service.ensure_first_admin(
            email=settings.FIRST_ADMIN_EMAIL,
            username=settings.FIRST_ADMIN_USERNAME,
            password=settings.FIRST_ADMIN_PASSWORD,
        )
        await db.commit()

    yield


app = FastAPI(
    title="MyBlog API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router)

# Serve uploaded files directly (nginx also serves these in production)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
