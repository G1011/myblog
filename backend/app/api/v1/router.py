from fastapi import APIRouter
from app.api.v1 import auth, articles, categories, tags, comments, upload, stats

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(articles.router)
router.include_router(categories.router)
router.include_router(tags.router)
router.include_router(comments.router)
router.include_router(upload.router)
router.include_router(stats.router)
