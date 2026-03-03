from fastapi import APIRouter, Depends
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.schemas.common import APIResponse
from app.services.category_service import CategoryService
from app.api.deps import get_category_service, get_current_user
from app.models.user import User
from typing import List

router = APIRouter()


@router.get("/categories", response_model=APIResponse[List[CategoryRead]])
async def list_categories(service: CategoryService = Depends(get_category_service)):
    rows = await service.list_all()
    data = [CategoryRead.model_validate({**c.__dict__, "article_count": count}) for c, count in rows]
    return APIResponse(data=data)


@router.get("/categories/{slug}", response_model=APIResponse[CategoryRead])
async def get_category(slug: str, service: CategoryService = Depends(get_category_service)):
    category = await service.get_by_slug(slug)
    return APIResponse(data=CategoryRead.model_validate({**category.__dict__, "article_count": 0}))


@router.post("/admin/categories", response_model=APIResponse[CategoryRead], status_code=201)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
    _: User = Depends(get_current_user),
):
    category = await service.create(data)
    return APIResponse(data=CategoryRead.model_validate({**category.__dict__, "article_count": 0}))


@router.put("/admin/categories/{category_id}", response_model=APIResponse[CategoryRead])
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
    _: User = Depends(get_current_user),
):
    category = await service.update(category_id, data)
    return APIResponse(data=CategoryRead.model_validate({**category.__dict__, "article_count": 0}))


@router.delete("/admin/categories/{category_id}", response_model=APIResponse[None])
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
    _: User = Depends(get_current_user),
):
    await service.delete(category_id)
    return APIResponse(message="Category deleted")
