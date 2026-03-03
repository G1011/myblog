from typing import List, Tuple, Optional
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate
from app.core.exceptions import NotFoundError


class CommentService:
    def __init__(self, repo: CommentRepository):
        self.repo = repo

    async def list_approved(self, article_id: int) -> List[Comment]:
        return await self.repo.list_approved_by_article(article_id)

    async def list_admin(
        self, status: Optional[str] = None, page: int = 1, size: int = 20
    ) -> Tuple[List[Comment], int]:
        offset = (page - 1) * size
        return await self.repo.list_admin(status=status, offset=offset, limit=size)

    async def submit(self, article_id: int, data: CommentCreate) -> Comment:
        comment_data = data.model_dump()
        return await self.repo.create(article_id=article_id, data=comment_data)

    async def approve(self, comment_id: int) -> Comment:
        comment = await self.repo.get_or_404(comment_id)
        return await self.repo.approve(comment)

    async def delete(self, comment_id: int) -> None:
        comment = await self.repo.get_or_404(comment_id)
        await self.repo.delete(comment)

    async def count_pending(self) -> int:
        return await self.repo.count_pending()
