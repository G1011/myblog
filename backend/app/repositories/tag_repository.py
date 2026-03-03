from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tag import Tag
from app.models.article import Article
from app.models.article_tag import article_tag_table
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tag, db)

    async def get_by_slug(self, slug: str) -> Optional[Tag]:
        result = await self.db.execute(select(Tag).where(Tag.slug == slug))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self.db.execute(select(Tag).where(Tag.name == name))
        return result.scalar_one_or_none()

    async def get_many_by_ids(self, ids: List[int]) -> List[Tag]:
        if not ids:
            return []
        result = await self.db.execute(select(Tag).where(Tag.id.in_(ids)))
        return list(result.scalars().all())

    async def list_with_counts(self) -> List[Tuple[Tag, int]]:
        stmt = (
            select(Tag, func.count(article_tag_table.c.article_id).label("article_count"))
            .outerjoin(article_tag_table, article_tag_table.c.tag_id == Tag.id)
            .outerjoin(Article, (Article.id == article_tag_table.c.article_id) & (Article.status == "published"))
            .group_by(Tag.id)
            .order_by(Tag.name)
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def create(self, name: str, slug: str) -> Tag:
        tag = Tag(name=name, slug=slug)
        return await self.save(tag)

    async def get_or_create_many(self, names: List[str]) -> List[Tag]:
        from slugify import slugify as _slugify
        tags: List[Tag] = []
        for name in names:
            tag = await self.get_by_name(name)
            if not tag:
                tag = await self.create(name=name, slug=_slugify(name))
            tags.append(tag)
        return tags
