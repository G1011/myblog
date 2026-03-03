from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)

    async def list_approved_by_article(self, article_id: int) -> List[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.article_id == article_id, Comment.is_approved == True, Comment.parent_id == None)
            .options(selectinload(Comment.replies))
            .order_by(Comment.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_admin(
        self,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Comment], int]:
        filters = []
        if status == "pending":
            filters.append(Comment.is_approved == False)
        elif status == "approved":
            filters.append(Comment.is_approved == True)

        count_stmt = select(func.count()).select_from(Comment)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(Comment)
            .options(selectinload(Comment.replies))
            .order_by(Comment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        for f in filters:
            stmt = stmt.where(f)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_with_replies(self, comment_id: int) -> Optional[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.id == comment_id)
            .options(selectinload(Comment.replies))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, article_id: int, data: dict) -> Comment:
        comment = Comment(article_id=article_id, **data)
        saved = await self.save(comment)
        return await self.get_with_replies(saved.id)

    async def approve(self, comment: Comment) -> Comment:
        comment.is_approved = True
        saved = await self.save(comment)
        return await self.get_with_replies(saved.id)

    async def count_pending(self) -> int:
        return await self.count(Comment.is_approved == False)
