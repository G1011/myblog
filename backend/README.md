# MyBlog Backend

基于 **FastAPI + SQLAlchemy 2.0 async + PostgreSQL** 构建的博客后端服务，提供 RESTful API，支持文章管理、分类标签、评论审核、全文搜索与图片上传。

---

## 架构说明

```
app/
├── main.py                  # FastAPI 应用工厂，注册路由、CORS、静态文件
├── core/
│   ├── config.py            # pydantic-settings 配置（读取 .env）
│   ├── security.py          # JWT 签发/验证、bcrypt 密码哈希
│   └── exceptions.py        # 自定义异常（NotFoundError、ConflictError）
├── db/
│   └── database.py          # 异步 Engine + get_db() Session 工厂
├── models/                  # SQLAlchemy ORM 映射
│   ├── base.py              # TimestampMixin（created_at / updated_at）
│   ├── user.py
│   ├── category.py
│   ├── tag.py
│   ├── article.py           # GIN 全文搜索索引
│   ├── article_tag.py       # M2M 联接表
│   └── comment.py           # 自引用嵌套评论
├── schemas/                 # Pydantic v2 DTO（请求/响应）
│   ├── common.py            # APIResponse[T]、PaginatedResponse[T]
│   ├── auth.py
│   ├── article.py
│   ├── category.py
│   ├── tag.py
│   └── comment.py
├── repositories/            # 数据访问层
│   ├── base.py              # BaseRepository[T]：get / save / delete / count
│   ├── user_repository.py
│   ├── article_repository.py  # 含 _base_query()（eagerly loaded 关系）
│   ├── category_repository.py
│   ├── tag_repository.py
│   └── comment_repository.py
├── services/                # 业务逻辑层
│   ├── auth_service.py      # 登录、token 颁发、首次管理员初始化
│   ├── article_service.py   # slug 生成、标签同步、发布/撤回
│   ├── category_service.py
│   ├── tag_service.py
│   └── comment_service.py   # 评论树构建、待审核计数
└── api/
    ├── deps.py              # FastAPI Depends 工厂：get_db、get_current_user、各 Service
    ├── health.py            # GET /health
    └── v1/
        ├── router.py        # 汇总所有子路由
        ├── auth.py
        ├── articles.py
        ├── categories.py
        ├── tags.py
        ├── comments.py
        ├── upload.py        # 图片上传（multipart/form-data）
        └── stats.py         # 管理员仪表盘统计
```

### 设计模式

| 模式 | 说明 |
|------|------|
| **Repository Pattern** | 每个实体对应一个 Repository，继承 `BaseRepository[T]`，隔离数据库访问逻辑 |
| **Service Layer** | 业务逻辑（slug 生成、关联关系同步、状态机）封装在 Service，不泄漏到路由层 |
| **Dependency Injection** | FastAPI `Depends` 工厂函数注入 DB Session → Repository → Service，便于测试替换 |
| **Eager Loading** | `ArticleRepository._base_query()` 通过 `selectinload` / `joinedload` 预加载关系，避免 `MissingGreenlet` 异常 |

---

## 数据库 Schema

| 表 | 关键字段 |
|----|---------|
| `users` | id, email(unique), username, hashed_password, is_active |
| `categories` | id, name(unique), slug(unique), description |
| `tags` | id, name(unique), slug(unique) |
| `articles` | id, title, slug(unique), summary, content_md, cover_image, status(`draft`/`published`), view_count, author_id→users, category_id→categories, published_at |
| `article_tags` | article_id, tag_id（多对多联接表）|
| `comments` | id, article_id→articles, parent_id→comments（自引用嵌套）, author_name, author_email, body, is_approved(默认 False) |

> **全文搜索**：在 `articles.(title || summary || content_md)` 上建 GIN tsvector 索引，支持中文分词。

---

## 环境要求

- Python 3.11+
- PostgreSQL 15+

---

## 本地启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
pip install "pydantic[email]" greenlet "sqlalchemy[asyncio]" "bcrypt==4.0.1"
```

### 2. 配置环境变量

复制并按需修改：

```bash
cp ../.env.example .env
```

主要配置项：

```ini
DATABASE_URL=postgresql+asyncpg://myblog:myblog_secret@localhost:5432/myblog
SECRET_KEY=your_secret_key_here
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=Admin@123456
CORS_ORIGINS=["http://localhost", "http://localhost:5173"]
```

### 3. 初始化数据库

```bash
# 创建 PostgreSQL 用户和数据库（首次）
psql -U postgres -c "CREATE USER myblog WITH PASSWORD 'myblog_secret';"
psql -U postgres -c "CREATE DATABASE myblog OWNER myblog;"

# 执行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后会自动创建首个管理员账号（`FIRST_ADMIN_*` 配置项）。

### 5. 访问文档

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

---

## Docker 部署

```bash
# 在项目根目录执行
cd ..
docker compose up --build
```

`entrypoint.sh` 会在 uvicorn 启动前自动执行 `alembic upgrade head`。

---

## API 接口说明

所有响应统一格式：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务健康状态 |

---

### 文章（公开）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/articles` | 已发布文章列表（分页、过滤、搜索）|
| GET | `/api/v1/articles/{slug}` | 文章详情（自增 view_count）|

**列表查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码，默认 1 |
| `size` | int | 每页数量，默认 10，最大 50 |
| `category` | string | 按分类 slug 过滤 |
| `tag` | string | 按标签 slug 过滤 |
| `q` | string | 全文搜索关键词 |

---

### 文章（管理员，需 JWT）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/articles` | 全部文章列表（含草稿）|
| GET | `/api/v1/admin/articles/{id}` | 文章详情（按 ID）|
| POST | `/api/v1/admin/articles` | 创建文章 |
| PUT | `/api/v1/admin/articles/{id}` | 更新文章 |
| DELETE | `/api/v1/admin/articles/{id}` | 删除文章 |
| PATCH | `/api/v1/admin/articles/{id}/publish` | 发布文章 |
| PATCH | `/api/v1/admin/articles/{id}/unpublish` | 撤回为草稿 |

**创建/更新文章请求体：**

```json
{
  "title": "文章标题",
  "summary": "摘要",
  "content_md": "# Markdown 正文",
  "cover_image": null,
  "status": "draft",
  "category_id": 1,
  "tag_ids": [1, 2, 3]
}
```

---

### 分类

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/categories` | 分类列表（含文章数）|
| GET | `/api/v1/categories/{slug}` | 单个分类详情 |
| POST | `/api/v1/admin/categories` | 创建分类（需 JWT）|
| PUT | `/api/v1/admin/categories/{id}` | 更新分类（需 JWT）|
| DELETE | `/api/v1/admin/categories/{id}` | 删除分类（需 JWT）|

**创建分类请求体：**

```json
{
  "name": "TechBlog",
  "slug": "tech",
  "description": "技术文章"
}
```

> `slug` 可选；未提供时自动由 `name` 生成。

---

### 标签

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/tags` | 标签列表（含文章数）|
| GET | `/api/v1/tags/{slug}` | 单个标签详情 |
| POST | `/api/v1/admin/tags` | 创建标签（需 JWT）|
| PUT | `/api/v1/admin/tags/{id}` | 更新标签（需 JWT）|
| DELETE | `/api/v1/admin/tags/{id}` | 删除标签（需 JWT）|

---

### 评论

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/articles/{id}/comments` | 已审核评论（树形结构）|
| POST | `/api/v1/articles/{id}/comments` | 提交评论（默认待审核）|
| GET | `/api/v1/admin/comments` | 全部评论列表（需 JWT）|
| PATCH | `/api/v1/admin/comments/{id}/approve` | 审核通过（需 JWT）|
| DELETE | `/api/v1/admin/comments/{id}` | 删除评论（需 JWT）|

**管理员评论列表查询参数：**

| 参数 | 值 | 说明 |
|------|-----|------|
| `status` | `pending` / `approved` / `all` | 按审核状态过滤 |

**提交评论请求体：**

```json
{
  "author_name": "读者",
  "author_email": "reader@example.com",
  "body": "评论内容",
  "parent_id": null
}
```

---

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录，返回 JWT |
| GET | `/api/v1/auth/me` | 当前登录用户信息（需 JWT）|

**登录请求体（表单格式）：**

```
username=admin@example.com&password=Admin@123456
```

**响应：**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### 文件上传

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/admin/upload/image` | 上传封面图（需 JWT，multipart/form-data）|

- 支持格式：JPEG、PNG、GIF、WebP
- 最大文件大小：10 MB
- 文件存储于 `uploads/` 目录，通过 `/uploads/{filename}` 访问

---

### 统计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/stats` | 仪表盘统计（需 JWT）|

**响应：**

```json
{
  "total_articles": 7,
  "published_articles": 7,
  "draft_articles": 0,
  "total_views": 123,
  "pending_comments": 2
}
```

---

## 认证说明

管理员接口需在 HTTP Header 中携带：

```
Authorization: Bearer <access_token>
```

Token 默认有效期 60 分钟（可通过 `ACCESS_TOKEN_EXPIRE_MINUTES` 配置）。

---

## 数据库迁移

```bash
# 生成新迁移（修改 models 后）
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚一步
alembic downgrade -1
```
