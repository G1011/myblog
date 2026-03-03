from fastapi import APIRouter, Depends
from app.schemas.tag import TagCreate, TagUpdate, TagRead
from app.schemas.common import APIResponse
from app.services.tag_service import TagService
from app.api.deps import get_tag_service, get_current_user
from app.models.user import User
from typing import List

router = APIRouter()


@router.get("/tags", response_model=APIResponse[List[TagRead]])
async def list_tags(service: TagService = Depends(get_tag_service)):
    rows = await service.list_all()
    data = [TagRead.model_validate({**t.__dict__, "article_count": count}) for t, count in rows]
    return APIResponse(data=data)


@router.get("/tags/{slug}", response_model=APIResponse[TagRead])
async def get_tag(slug: str, service: TagService = Depends(get_tag_service)):
    tag = await service.get_by_slug(slug)
    return APIResponse(data=TagRead.model_validate({**tag.__dict__, "article_count": 0}))


@router.post("/admin/tags", response_model=APIResponse[TagRead], status_code=201)
async def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_user),
):
    tag = await service.create(data)
    return APIResponse(data=TagRead.model_validate({**tag.__dict__, "article_count": 0}))


@router.put("/admin/tags/{tag_id}", response_model=APIResponse[TagRead])
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_user),
):
    tag = await service.update(tag_id, data)
    return APIResponse(data=TagRead.model_validate({**tag.__dict__, "article_count": 0}))


@router.delete("/admin/tags/{tag_id}", response_model=APIResponse[None])
async def delete_tag(
    tag_id: int,
    service: TagService = Depends(get_tag_service),
    _: User = Depends(get_current_user),
):
    await service.delete(tag_id)
    return APIResponse(message="Tag deleted")
