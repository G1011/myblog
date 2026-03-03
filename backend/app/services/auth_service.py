from typing import Optional
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, hash_password
from app.core.exceptions import UnauthorizedError


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        return user

    def create_token(self, user: User) -> str:
        return create_access_token({"sub": str(user.id), "email": user.email})

    async def ensure_first_admin(self, email: str, username: str, password: str) -> None:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            return
        hashed = hash_password(password)
        await self.user_repo.create(
            email=email,
            username=username,
            hashed_password=hashed,
            is_superuser=True,
        )
