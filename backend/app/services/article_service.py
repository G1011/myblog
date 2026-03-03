from typing import Optional, List, Tuple, Union
from datetime import datetime
from slugify import slugify
from app.models.article import Article
from app.repositories.article_repository import ArticleRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleRead, ArticleSummary
from app.core.exceptions import NotFoundError, ConflictError
from app.core.file_storage import ArticleFileStorage
import logging

logger = logging.getLogger(__name__)


class ArticleService:
    def __init__(
        self,
        article_repo: ArticleRepository,
        tag_repo: TagRepository,
        file_storage: Optional[ArticleFileStorage] = None,
        category_repo: Optional[CategoryRepository] = None,
    ):
        self.article_repo = article_repo
        self.tag_repo = tag_repo
        self.file_storage = file_storage
        self.category_repo = category_repo

    async def _generate_unique_slug(self, title: str, exclude_id: Optional[int] = None) -> str:
        base_slug = slugify(title)
        slug = base_slug
        counter = 2
        while True:
            existing = await self.article_repo.get_by_slug(slug)
            if not existing or (exclude_id and existing.id == exclude_id):
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    async def list_published(
        self,
        page: int = 1,
        size: int = 10,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        q: Optional[str] = None,
    ) -> Tuple[List[Union[Article, ArticleSummary]], int]:
        offset = (page - 1) * size
        try:
            items, total = await self.article_repo.list_published(
                offset=offset, limit=size,
                category_slug=category, tag_slug=tag, search_query=q,
            )
            return items, total
        except NotFoundError:
            raise
        except Exception:
            if self.file_storage:
                logger.warning("DB unavailable, falling back to file storage for list_published")
                all_items = await self.file_storage.list_all(
                    category_slug=category, tag_slug=tag, q=q
                )
                total = len(all_items)
                return all_items[offset: offset + size], total
            raise

    async def list_all(self, page: int = 1, size: int = 20) -> Tuple[List[Article], int]:
        offset = (page - 1) * size
        return await self.article_repo.list_all(offset=offset, limit=size)

    async def get_published_by_slug(self, slug: str) -> Union[Article, ArticleRead]:
        try:
            article = await self.article_repo.get_by_slug(slug)
            if not article or article.status != "published":
                raise NotFoundError(f"Article '{slug}' not found")
            await self.article_repo.increment_view_count(article.id)
            return article
        except NotFoundError:
            raise
        except Exception:
            if self.file_storage:
                logger.warning("DB unavailable, falling back to file storage for slug=%s", slug)
                fallback = await self.file_storage.read_by_slug(slug)
                if not fallback or fallback.status != "published":
                    raise NotFoundError(f"Article '{slug}' not found")
                return fallback
            raise

    async def get_by_id(self, article_id: int) -> Article:
        article = await self.article_repo.get_with_relations(article_id)
        if not article:
            raise NotFoundError(f"Article with id={article_id} not found")
        return article

    async def create(self, data: ArticleCreate, author_id: int) -> Article:
        slug = await self._generate_unique_slug(data.title)
        tags = await self.tag_repo.get_many_by_ids(data.tag_ids)
        article_data = data.model_dump(exclude={"tag_ids"})
        article_data["slug"] = slug
        article_data["author_id"] = author_id
        if article_data.get("status") == "published":
            article_data["published_at"] = datetime.utcnow()
        article = await self.article_repo.create(article_data, tags)
        full = await self.article_repo.get_with_relations(article.id)
        if self.file_storage:
            try:
                await self.file_storage.save(full)
            except Exception:
                logger.exception("Failed to persist article file for slug=%s", slug)
        return full

    async def update(self, article_id: int, data: ArticleUpdate) -> Article:
        article = await self.article_repo.get_with_relations(article_id)
        if not article:
            raise NotFoundError(f"Article with id={article_id} not found")

        old_slug = article.slug
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})

        # Handle publish transition
        if update_data.get("status") == "published" and article.status == "draft":
            update_data["published_at"] = datetime.utcnow()
        elif update_data.get("status") == "draft":
            update_data["published_at"] = None

        # Update title → regenerate slug
        if "title" in update_data:
            update_data["slug"] = await self._generate_unique_slug(
                update_data["title"], exclude_id=article_id
            )

        tags = None
        if data.tag_ids is not None:
            tags = await self.tag_repo.get_many_by_ids(data.tag_ids)

        await self.article_repo.update(article, update_data, tags)
        full = await self.article_repo.get_with_relations(article_id)

        if self.file_storage:
            try:
                new_slug = full.slug
                if new_slug != old_slug:
                    await self.file_storage.rename(old_slug, new_slug)
                await self.file_storage.save(full)
            except Exception:
                logger.exception("Failed to update article file for id=%d", article_id)

        return full

    async def delete(self, article_id: int) -> None:
        article = await self.article_repo.get_or_404(article_id)
        slug = article.slug
        await self.article_repo.delete(article)
        if self.file_storage:
            try:
                await self.file_storage.delete(slug)
            except Exception:
                logger.exception("Failed to delete article file for slug=%s", slug)

    async def publish(self, article_id: int) -> Article:
        article = await self.article_repo.get_or_404(article_id)
        article.status = "published"
        if not article.published_at:
            article.published_at = datetime.utcnow()
        await self.article_repo.save(article)
        full = await self.article_repo.get_with_relations(article_id)
        if self.file_storage:
            try:
                await self.file_storage.save(full)
            except Exception:
                logger.exception("Failed to persist article file after publish for id=%d", article_id)
        return full

    async def unpublish(self, article_id: int) -> Article:
        article = await self.article_repo.get_or_404(article_id)
        article.status = "draft"
        await self.article_repo.save(article)
        full = await self.article_repo.get_with_relations(article_id)
        if self.file_storage:
            try:
                await self.file_storage.save(full)
            except Exception:
                logger.exception("Failed to persist article file after unpublish for id=%d", article_id)
        return full

    async def create_from_file(self, content: str, author_id: int) -> Article:
        """
        Create an article from an uploaded .md file with YAML frontmatter.
        frontmatter must contain 'title'. Other fields are optional.
        """
        meta, body = ArticleFileStorage.parse_upload(content)

        # Resolve category
        category_id: Optional[int] = None
        if self.category_repo and meta.get("category"):
            category = await self.category_repo.get_by_slug(meta["category"])
            if category:
                category_id = category.id

        # Resolve tags (get_or_create)
        tag_ids: List[int] = []
        if meta.get("tags"):
            tag_names = [str(t) for t in meta["tags"]]
            tags = await self.tag_repo.get_or_create_many(tag_names)
            tag_ids = [t.id for t in tags]

        article_data = ArticleCreate(
            title=str(meta["title"]),
            summary=meta.get("summary") or None,
            content_md=body,
            cover_image=meta.get("cover_image") or None,
            status=str(meta.get("status", "draft")),
            category_id=category_id,
            tag_ids=tag_ids,
        )
        return await self.create(article_data, author_id=author_id)
