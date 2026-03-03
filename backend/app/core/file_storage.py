"""
Article file-system persistence layer.
Stores each article as a .md file with YAML frontmatter under ARTICLES_DIR.
Used as a fallback when the database is unavailable.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional, Tuple

import aiofiles
import frontmatter

if TYPE_CHECKING:
    from app.core.config import Settings
    from app.models.article import Article
    from app.schemas.article import ArticleRead, ArticleSummary


def _isoformat(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


class ArticleFileStorage:
    def __init__(self, settings: "Settings") -> None:
        self._dir = settings.ARTICLES_DIR
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, slug: str) -> str:
        return os.path.join(self._dir, f"{slug}.md")

    # ── write helpers ──────────────────────────────────────────────────────────

    def _build_frontmatter(self, article: "Article") -> dict:
        return {
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "status": article.status,
            "author": article.author.username if article.author else None,
            "category": article.category.slug if article.category else None,
            "tags": [t.name for t in (article.tags or [])],
            "cover_image": article.cover_image,
            "published_at": _isoformat(article.published_at),
            "created_at": _isoformat(article.created_at),
        }

    async def save(self, article: "Article") -> None:
        """Persist article to <slug>.md (create or overwrite)."""
        meta = self._build_frontmatter(article)
        post = frontmatter.Post(article.content_md or "", **meta)
        content = frontmatter.dumps(post)
        async with aiofiles.open(self._path(article.slug), "w", encoding="utf-8") as f:
            await f.write(content)

    async def delete(self, slug: str) -> None:
        """Remove .md file; silently ignore if it doesn't exist."""
        path = self._path(slug)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    async def rename(self, old_slug: str, new_slug: str) -> None:
        """Rename file when slug changes."""
        old_path = self._path(old_slug)
        new_path = self._path(new_slug)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)

    # ── read helpers ───────────────────────────────────────────────────────────

    def _parse_file(self, path: str) -> Optional[Tuple[dict, str]]:
        """Return (metadata_dict, body) or None on parse error."""
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
            post = frontmatter.loads(raw)
            return dict(post.metadata), post.content
        except Exception:
            return None

    def _meta_to_article_read(self, meta: dict, body: str) -> "ArticleRead":
        from app.schemas.article import ArticleRead, CategoryBrief, TagBrief, AuthorBrief

        category_slug = meta.get("category")
        category = CategoryBrief(id=0, name=category_slug or "", slug=category_slug or "") if category_slug else None

        tag_names: List[str] = meta.get("tags") or []
        tags = [TagBrief(id=0, name=t, slug=t) for t in tag_names]

        author_name = meta.get("author")
        author = AuthorBrief(id=0, username=author_name or "") if author_name else None

        def _parse_dt(v) -> Optional[datetime]:
            if v is None:
                return None
            if isinstance(v, datetime):
                return v
            try:
                return datetime.fromisoformat(str(v))
            except Exception:
                return None

        return ArticleRead(
            id=0,
            title=meta.get("title", ""),
            slug=meta.get("slug", ""),
            summary=meta.get("summary"),
            cover_image=meta.get("cover_image"),
            status=meta.get("status", "published"),
            view_count=0,
            published_at=_parse_dt(meta.get("published_at")),
            created_at=_parse_dt(meta.get("created_at")) or datetime.now(timezone.utc),
            author=author,
            category=category,
            tags=tags,
            content_md=body,
        )

    def _meta_to_summary(self, meta: dict) -> "ArticleSummary":
        from app.schemas.article import ArticleSummary, CategoryBrief, TagBrief, AuthorBrief

        category_slug = meta.get("category")
        category = CategoryBrief(id=0, name=category_slug or "", slug=category_slug or "") if category_slug else None

        tag_names: List[str] = meta.get("tags") or []
        tags = [TagBrief(id=0, name=t, slug=t) for t in tag_names]

        author_name = meta.get("author")
        author = AuthorBrief(id=0, username=author_name or "") if author_name else None

        def _parse_dt(v) -> Optional[datetime]:
            if v is None:
                return None
            if isinstance(v, datetime):
                return v
            try:
                return datetime.fromisoformat(str(v))
            except Exception:
                return None

        return ArticleSummary(
            id=0,
            title=meta.get("title", ""),
            slug=meta.get("slug", ""),
            summary=meta.get("summary"),
            cover_image=meta.get("cover_image"),
            status=meta.get("status", "published"),
            view_count=0,
            published_at=_parse_dt(meta.get("published_at")),
            created_at=_parse_dt(meta.get("created_at")) or datetime.now(timezone.utc),
            author=author,
            category=category,
            tags=tags,
        )

    async def read_by_slug(self, slug: str) -> Optional["ArticleRead"]:
        """Parse <slug>.md → ArticleRead; returns None if not found."""
        path = self._path(slug)
        if not os.path.exists(path):
            return None
        result = self._parse_file(path)
        if result is None:
            return None
        meta, body = result
        return self._meta_to_article_read(meta, body)

    async def read_raw(self, slug: str) -> Optional[str]:
        """Return raw file content for download; None if not found."""
        path = self._path(slug)
        if not os.path.exists(path):
            return None
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return await f.read()

    async def list_all(
        self,
        category_slug: Optional[str] = None,
        tag_slug: Optional[str] = None,
        q: Optional[str] = None,
    ) -> List["ArticleSummary"]:
        """Scan directory and return matching published summaries."""
        items: List["ArticleSummary"] = []
        if not os.path.isdir(self._dir):
            return items
        for fname in os.listdir(self._dir):
            if not fname.endswith(".md"):
                continue
            result = self._parse_file(os.path.join(self._dir, fname))
            if result is None:
                continue
            meta, body = result
            if meta.get("status") != "published":
                continue
            if category_slug and meta.get("category") != category_slug:
                continue
            if tag_slug:
                tag_names = [t.lower() for t in (meta.get("tags") or [])]
                if tag_slug.lower() not in tag_names:
                    continue
            if q:
                q_lower = q.lower()
                searchable = " ".join(filter(None, [
                    meta.get("title", ""),
                    meta.get("summary", ""),
                    body,
                ])).lower()
                if q_lower not in searchable:
                    continue
            items.append(self._meta_to_summary(meta))
        items.sort(key=lambda a: a.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return items

    # ── upload helper ──────────────────────────────────────────────────────────

    @staticmethod
    def parse_upload(content: str) -> Tuple[dict, str]:
        """
        Parse a user-uploaded .md file.
        Returns (metadata_dict, body_content).
        Raises ValueError if 'title' is missing from frontmatter.
        """
        try:
            post = frontmatter.loads(content)
        except Exception as exc:
            raise ValueError(f"Failed to parse frontmatter: {exc}") from exc
        meta = dict(post.metadata)
        if not meta.get("title"):
            raise ValueError("Uploaded .md file must have 'title' in frontmatter")
        return meta, post.content
