from typing import Optional, List, Sequence, Tuple
from sqlalchemy import select, func, or_, text
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.article import Article
from app.models.article_tag import article_tag_table
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    def __init__(self, db: AsyncSession):
        super().__init__(Article, db)

    def _base_query(self):
        return select(Article).options(
            selectinload(Article.tags),
            joinedload(Article.author),
            joinedload(Article.category),
        )

    async def get_by_slug(self, slug: str) -> Optional[Article]:
        stmt = self._base_query().where(Article.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_relations(self, id: int) -> Optional[Article]:
        stmt = self._base_query().where(Article.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_published(
        self,
        offset: int = 0,
        limit: int = 10,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> Tuple[List[Article], int]:
        filters = [Article.status == "published"]

        if category_slug:
            from app.models.category import Category
            filters.append(
                Article.category_id.in_(
                    select(Category.id).where(Category.slug == category_slug)
                )
            )

        if tag_slug:
            from app.models.tag import Tag
            tag_subq = (
                select(article_tag_table.c.article_id)
                .join(Tag, Tag.id == article_tag_table.c.tag_id)
                .where(Tag.slug == tag_slug)
            )
            filters.append(Article.id.in_(tag_subq))

        if search_query:
            search_filter = or_(
                Article.title.ilike(f"%{search_query}%"),
                Article.summary.ilike(f"%{search_query}%"),
                Article.content_md.ilike(f"%{search_query}%"),
            )
            filters.append(search_filter)

        count_stmt = select(func.count()).select_from(Article)
        for f in filters:
            count_stmt = count_stmt.where(f)
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = self._base_query()
        for f in filters:
            stmt = stmt.where(f)
        stmt = stmt.order_by(Article.published_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def list_all(self, offset: int = 0, limit: int = 20) -> Tuple[List[Article], int]:
        total = await self.count()
        stmt = (
            self._base_query()
            .order_by(Article.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, data: dict, tags: List) -> Article:
        tag_ids = data.pop("tag_ids", [])
        article = Article(**data)
        article.tags = tags
        return await self.save(article)

    async def update(self, article: Article, data: dict, tags: Optional[List] = None) -> Article:
        for key, value in data.items():
            setattr(article, key, value)
        if tags is not None:
            article.tags = tags
        return await self.save(article)

    async def increment_view_count(self, article_id: int) -> None:
        stmt = select(Article).where(Article.id == article_id)
        result = await self.db.execute(stmt)
        article = result.scalar_one_or_none()
        if article:
            article.view_count += 1
            await self.db.flush()
