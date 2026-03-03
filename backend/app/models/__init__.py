# Import all models so Alembic can detect them for autogenerate
from app.models.user import User
from app.models.article_tag import article_tag_table
from app.models.category import Category
from app.models.tag import Tag
from app.models.article import Article
from app.models.comment import Comment

__all__ = ["User", "Category", "Tag", "Article", "Comment", "article_tag_table"]
