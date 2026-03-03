from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.base import TimestampMixin
from app.models.article_tag import article_tag_table


class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    summary = Column(String(500), nullable=True)
    content_md = Column(Text, nullable=False)
    cover_image = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="draft")  # 'draft' | 'published'
    view_count = Column(Integer, nullable=False, default=0)
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    author = relationship("User", back_populates="articles", lazy="select")
    category = relationship("Category", back_populates="articles", lazy="select")
    tags = relationship(
        "Tag",
        secondary=article_tag_table,
        back_populates="articles",
        lazy="selectin",
    )
    comments = relationship(
        "Comment",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="select",
    )
