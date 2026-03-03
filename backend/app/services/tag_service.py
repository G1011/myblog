from typing import List, Tuple
from slugify import slugify
from app.models.tag import Tag
from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagCreate, TagUpdate
from app.core.exceptions import ConflictError, NotFoundError


class TagService:
    def __init__(self, repo: TagRepository):
        self.repo = repo

    async def list_all(self) -> List[Tuple[Tag, int]]:
        return await self.repo.list_with_counts()

    async def get_by_slug(self, slug: str) -> Tag:
        tag = await self.repo.get_by_slug(slug)
        if not tag:
            raise NotFoundError(f"Tag '{slug}' not found")
        return tag

    async def create(self, data: TagCreate) -> Tag:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictError(f"Tag '{data.name}' already exists")
        slug = slugify(data.name)
        return await self.repo.create(name=data.name, slug=slug)

    async def update(self, tag_id: int, data: TagUpdate) -> Tag:
        tag = await self.repo.get_or_404(tag_id)
        if data.name != tag.name:
            existing = await self.repo.get_by_name(data.name)
            if existing:
                raise ConflictError(f"Tag '{data.name}' already exists")
            tag.name = data.name
            tag.slug = slugify(data.name)
        return await self.repo.save(tag)

    async def delete(self, tag_id: int) -> None:
        tag = await self.repo.get_or_404(tag_id)
        await self.repo.delete(tag)

    async def get_tags_by_ids(self, ids: List[int]) -> List[Tag]:
        return await self.repo.get_many_by_ids(ids)
