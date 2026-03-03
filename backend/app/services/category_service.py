from typing import List, Tuple
from slugify import slugify
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import ConflictError, NotFoundError


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def list_all(self) -> List[Tuple[Category, int]]:
        return await self.repo.list_with_counts()

    async def get_by_slug(self, slug: str) -> Category:
        cat = await self.repo.get_by_slug(slug)
        if not cat:
            raise NotFoundError(f"Category '{slug}' not found")
        return cat

    async def create(self, data: CategoryCreate) -> Category:
        existing = await self.repo.get_by_name(data.name)
        if existing:
            raise ConflictError(f"Category '{data.name}' already exists")
        slug = slugify(data.slug) if data.slug else slugify(data.name)
        return await self.repo.create(name=data.name, slug=slug, description=data.description)

    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self.repo.get_or_404(category_id)
        if data.name and data.name != category.name:
            existing = await self.repo.get_by_name(data.name)
            if existing:
                raise ConflictError(f"Category '{data.name}' already exists")
            category.name = data.name
            category.slug = slugify(data.name)
        if data.description is not None:
            category.description = data.description
        return await self.repo.save(category)

    async def delete(self, category_id: int) -> None:
        category = await self.repo.get_or_404(category_id)
        await self.repo.delete(category)
