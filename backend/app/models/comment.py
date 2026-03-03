from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.base import TimestampMixin


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_approved = Column(Boolean, nullable=False, default=False, index=True)

    article = relationship("Article", back_populates="comments")

    # Self-referential: replies are child comments
    replies = relationship(
        "Comment",
        primaryjoin="Comment.parent_id == Comment.id",
        foreign_keys="Comment.parent_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
