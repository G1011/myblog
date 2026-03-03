from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.config import settings
from app.core.file_storage import ArticleFileStorage
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.article_repository import ArticleRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.comment_repository import CommentRepository
from app.services.auth_service import AuthService
from app.services.article_service import ArticleService
from app.services.tag_service import TagService
from app.services.category_service import CategoryService
from app.services.comment_service import CommentService

_article_file_storage = ArticleFileStorage(settings)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# Service factory dependencies
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


def get_article_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(
        ArticleRepository(db),
        TagRepository(db),
        file_storage=_article_file_storage,
        category_repo=CategoryRepository(db),
    )


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(db))


def get_tag_service(db: AsyncSession = Depends(get_db)) -> TagService:
    return TagService(TagRepository(db))


def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(CommentRepository(db))
