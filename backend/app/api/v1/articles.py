from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleSummary, ArticleRead
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.article_service import ArticleService
from app.api.deps import get_article_service, get_current_user, _article_file_storage
from app.models.user import User
import math
import io

router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────────────────

@router.get("/articles", response_model=APIResponse[PaginatedResponse[ArticleSummary]])
async def list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    service: ArticleService = Depends(get_article_service),
):
    items, total = await service.list_published(page=page, size=size, category=category, tag=tag, q=q)
    summaries = [
        a if isinstance(a, ArticleSummary) else ArticleSummary.model_validate(a)
        for a in items
    ]
    return APIResponse(data=PaginatedResponse(
        items=summaries,
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    ))


@router.get("/articles/{slug}", response_model=APIResponse[ArticleRead])
async def get_article(slug: str, service: ArticleService = Depends(get_article_service)):
    article = await service.get_published_by_slug(slug)
    if isinstance(article, ArticleRead):
        return APIResponse(data=article)
    return APIResponse(data=ArticleRead.model_validate(article))


# ── Admin endpoints ───────────────────────────────────────────────────────────

@router.get("/admin/articles", response_model=APIResponse[PaginatedResponse[ArticleSummary]])
async def admin_list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    items, total = await service.list_all(page=page, size=size)
    return APIResponse(data=PaginatedResponse(
        items=[ArticleSummary.model_validate(a) for a in items],
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    ))


@router.get("/admin/articles/{article_id}", response_model=APIResponse[ArticleRead])
async def admin_get_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    article = await service.get_by_id(article_id)
    return APIResponse(data=ArticleRead.model_validate(article))


@router.post("/admin/articles", response_model=APIResponse[ArticleRead], status_code=201)
async def create_article(
    data: ArticleCreate,
    service: ArticleService = Depends(get_article_service),
    current_user: User = Depends(get_current_user),
):
    article = await service.create(data, author_id=current_user.id)
    return APIResponse(data=ArticleRead.model_validate(article))


@router.post("/admin/articles/upload", response_model=APIResponse[ArticleRead], status_code=201)
async def upload_article_md(
    file: UploadFile = File(...),
    service: ArticleService = Depends(get_article_service),
    current_user: User = Depends(get_current_user),
):
    """Upload a .md file with YAML frontmatter to create a new article."""
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are accepted")
    raw_bytes = await file.read()
    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    try:
        article = await service.create_from_file(content, author_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return APIResponse(data=ArticleRead.model_validate(article))


@router.put("/admin/articles/{article_id}", response_model=APIResponse[ArticleRead])
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    article = await service.update(article_id, data)
    return APIResponse(data=ArticleRead.model_validate(article))


@router.delete("/admin/articles/{article_id}", response_model=APIResponse[None])
async def delete_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    await service.delete(article_id)
    return APIResponse(message="Article deleted")


@router.patch("/admin/articles/{article_id}/publish", response_model=APIResponse[ArticleSummary])
async def publish_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    article = await service.publish(article_id)
    return APIResponse(data=ArticleSummary.model_validate(article))


@router.patch("/admin/articles/{article_id}/unpublish", response_model=APIResponse[ArticleSummary])
async def unpublish_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    article = await service.unpublish(article_id)
    return APIResponse(data=ArticleSummary.model_validate(article))


@router.get("/admin/articles/{article_id}/download")
async def download_article_md(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
    _: User = Depends(get_current_user),
):
    """Download the persisted .md file for an article."""
    article = await service.get_by_id(article_id)
    slug = article.slug
    content = await _article_file_storage.read_raw(slug)
    if content is None:
        raise HTTPException(status_code=404, detail="Markdown file not found on disk")
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{slug}.md"'},
    )
