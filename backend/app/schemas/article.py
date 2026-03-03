from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.tag import TagRead
from app.schemas.category import CategoryRead


class ArticleCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    content_md: str
    cover_image: Optional[str] = None
    status: str = "draft"
    category_id: Optional[int] = None
    tag_ids: List[int] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content_md: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TagBrief(BaseModel):
    id: int
    name: str
    slug: str
    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    name: str
    slug: str
    model_config = {"from_attributes": True}


class AuthorBrief(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}


class ArticleSummary(BaseModel):
    """Used in list views — no full content"""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    status: str
    view_count: int
    published_at: Optional[datetime] = None
    created_at: datetime
    author: Optional[AuthorBrief] = None
    category: Optional[CategoryBrief] = None
    tags: List[TagBrief] = []

    model_config = {"from_attributes": True}


class ArticleRead(ArticleSummary):
    """Full article with content"""
    content_md: str
