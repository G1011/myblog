from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.models.article import Article
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()

    async def list_with_counts(self) -> List[Tuple[Category, int]]:
        stmt = (
            select(Category, func.count(Article.id).label("article_count"))
            .outerjoin(Article, (Article.category_id == Category.id) & (Article.status == "published"))
            .group_by(Category.id)
            .order_by(Category.name)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def create(self, name: str, slug: str, description: Optional[str] = None) -> Category:
        category = Category(name=name, slug=slug, description=description)
        return await self.save(category)
