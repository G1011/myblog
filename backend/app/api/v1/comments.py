from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from app.schemas.comment import CommentCreate, CommentRead, CommentAdminRead
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.comment_service import CommentService
from app.api.deps import get_comment_service, get_current_user
from app.models.user import User
import math

router = APIRouter()


@router.get("/articles/{article_id}/comments", response_model=APIResponse[List[CommentRead]])
async def list_comments(
    article_id: int,
    service: CommentService = Depends(get_comment_service),
):
    comments = await service.list_approved(article_id)
    return APIResponse(data=[CommentRead.model_validate(c) for c in comments])


@router.post("/articles/{article_id}/comments", response_model=APIResponse[CommentRead], status_code=201)
async def submit_comment(
    article_id: int,
    data: CommentCreate,
    service: CommentService = Depends(get_comment_service),
):
    comment = await service.submit(article_id, data)
    return APIResponse(
        data=CommentRead.model_validate(comment),
        message="Comment submitted and awaiting moderation",
    )


@router.get("/admin/comments", response_model=APIResponse[PaginatedResponse[CommentAdminRead]])
async def admin_list_comments(
    status: Optional[str] = Query(None, pattern="^(pending|approved|all)?$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: CommentService = Depends(get_comment_service),
    _: User = Depends(get_current_user),
):
    items, total = await service.list_admin(status=status, page=page, size=size)
    return APIResponse(data=PaginatedResponse(
        items=[CommentAdminRead.model_validate(c) for c in items],
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    ))


@router.patch("/admin/comments/{comment_id}/approve", response_model=APIResponse[CommentRead])
async def approve_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    _: User = Depends(get_current_user),
):
    comment = await service.approve(comment_id)
    return APIResponse(data=CommentRead.model_validate(comment))


@router.delete("/admin/comments/{comment_id}", response_model=APIResponse[None])
async def delete_comment(
    comment_id: int,
    service: CommentService = Depends(get_comment_service),
    _: User = Depends(get_current_user),
):
    await service.delete(comment_id)
    return APIResponse(message="Comment deleted")
