from fastapi import APIRouter, Depends
from app.schemas.auth import LoginRequest, TokenResponse, UserRead
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.api.deps import get_auth_service, get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    user = await service.authenticate(data.email, data.password)
    token = service.create_token(user)
    return APIResponse(data=TokenResponse(access_token=token))


@router.get("/me", response_model=APIResponse[UserRead])
async def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(data=UserRead.model_validate(current_user))
