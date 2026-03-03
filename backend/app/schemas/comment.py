from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class CommentCreate(BaseModel):
    author_name: str
    author_email: EmailStr
    body: str
    parent_id: Optional[int] = None


class CommentRead(BaseModel):
    id: int
    article_id: int
    parent_id: Optional[int] = None
    author_name: str
    body: str
    is_approved: bool
    created_at: datetime
    replies: List["CommentRead"] = []

    model_config = {"from_attributes": True}


class CommentAdminRead(CommentRead):
    """Admin view includes email"""
    author_email: str


CommentRead.model_rebuild()
