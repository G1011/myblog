from pydantic import BaseModel
from typing import Optional


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class TagRead(BaseModel):
    id: int
    name: str
    slug: str
    article_count: int = 0

    model_config = {"from_attributes": True}
