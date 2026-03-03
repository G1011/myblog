from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.article import Article
from app.models.comment import Comment
from app.schemas.common import APIResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/admin/stats", response_model=APIResponse[dict])
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    total_articles = (await db.execute(select(func.count()).select_from(Article))).scalar_one()
    published_articles = (
        await db.execute(select(func.count()).select_from(Article).where(Article.status == "published"))
    ).scalar_one()
    total_views = (await db.execute(select(func.sum(Article.view_count)).select_from(Article))).scalar_one() or 0
    pending_comments = (
        await db.execute(select(func.count()).select_from(Comment).where(Comment.is_approved == False))
    ).scalar_one()

    return APIResponse(data={
        "total_articles": total_articles,
        "published_articles": published_articles,
        "draft_articles": total_articles - published_articles,
        "total_views": total_views,
        "pending_comments": pending_comments,
    })
