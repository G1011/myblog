# MyBlog

一个极简风格的全栈个人博客系统，支持 Markdown 写作、深色/浅色双主题、管理员后台，一键 Docker Compose 部署。

## 预览

| 公开页面 | 管理后台 |
|---------|---------|
| 极简黑白风格，深色/浅色主题 | Markdown 双栏编辑器（实时预览） |
| 文章分类（TechBlog / LifeBlog） | 文章、分类、标签、评论管理 |
| 评论系统（游客提交、管理员审核） | 数据仪表盘 |
| 全文搜索 | 文章一键导出 / 上传 .md 文件 |

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 · TypeScript · Vite · Pinia · Vue Router · Tailwind CSS |
| 后端 | Python 3.11 · FastAPI · SQLAlchemy 2.0 (async) · asyncpg |
| 数据库 | PostgreSQL 15 |
| 反向代理 | Nginx 1.25 |
| 部署 | Docker · Docker Compose |

---

## 项目架构

### 目录结构

```
myblog/
├── docker-compose.yml        # 一键启动所有服务
├── .env.example              # 环境变量模板
├── deploy.sh                 # 一键部署脚本（生产）
├── nginx/
│   ├── nginx.conf            # 反向代理 + 静态文件
│   └── Dockerfile            # 多阶段：Node 构建前端 → Nginx 托管
├── backend/
│   ├── requirements.txt
│   ├── entrypoint.sh         # 启动前执行 alembic upgrade head
│   ├── alembic/              # 数据库迁移
│   └── app/
│       ├── main.py           # FastAPI 应用工厂
│       ├── core/             # 配置、JWT、异常、文件存储
│       ├── db/               # 异步引擎 + Session
│       ├── models/           # SQLAlchemy ORM 模型
│       ├── schemas/          # Pydantic v2 DTO
│       ├── repositories/     # 数据访问层（Repository Pattern）
│       ├── services/         # 业务逻辑层（Service Layer）
│       └── api/v1/           # FastAPI 路由
└── frontend/
    ├── public/               # 静态资源（avatar、favicon）
    └── src/
        ├── api/              # Axios 封装
        ├── stores/           # Pinia（auth、theme）
        ├── router/           # 路由 + 路由守卫
        ├── composables/      # 可复用逻辑（Markdown、分页、搜索）
        ├── components/       # 通用 / 文章 / 评论 / 管理 组件
        └── views/            # 公开页面 + 管理后台页面
```

### 服务拓扑

```
Browser
   │
   ▼
Nginx :80
   ├── /api/*  ──→  FastAPI Backend :8000  ──→  PostgreSQL :5432
   ├── /uploads/    (静态文件直接服务)
   └── /            (Vue SPA 静态文件)
```

**网络隔离**：Postgres 与 Backend 在 `internal` 网络中，仅 Nginx 通过 `external` 网络暴露至宿主机，数据库不对外开放端口。

### 数据库模型

| 表 | 关键字段 |
|----|---------|
| `users` | id, email, username, hashed_password, is_active, is_superuser |
| `categories` | id, name, slug |
| `tags` | id, name, slug |
| `articles` | id, title, slug, summary, content_md, status, view_count, author_id, category_id, published_at |
| `article_tags` | article_id, tag_id（多对多联接表） |
| `comments` | id, article_id, parent_id（嵌套回复）, author_name, author_email, body, is_approved |

全文搜索：在 `(title \|\| summary \|\| content_md)` 上建 PostgreSQL GIN tsvector 索引。

### 设计模式

- **Repository Pattern**：每个实体对应一个 Repository，继承 `BaseRepository[T]`，隔离数据库访问
- **Service Layer**：业务逻辑（slug 生成、标签同步、评论树构建）封装在 Service 中，不泄漏到路由层
- **Dependency Injection**：通过 FastAPI `Depends` 组装依赖链 `Route → Service → Repository → DB`
- **Markdown 文件持久化**：文章保存时同步写入 `backend/content/articles/{slug}.md`（含 YAML frontmatter），数据库不可用时自动降级从文件读取

---

## 本地开发

### 前置要求

- Docker Desktop ≥ 4.x
- （可选）Node.js 22 + Python 3.11（本地调试用）

### 启动

```bash
# 1. 克隆项目
git clone https://github.com/G1011/myblog.git
cd myblog

# 2. 配置环境变量
cp .env.example .env
# 可直接使用默认值，或按需修改

# 3. 一键启动
docker compose up --build

# 访问地址
# 博客首页:  http://localhost
# 管理后台:  http://localhost/admin/login
```

> **macOS 用户**：若 Docker Desktop 默认未加入 PATH，可使用完整路径：
> ```bash
> PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH" docker compose up --build
> ```

### 默认管理员账号

| 字段 | 值 |
|------|----|
| 邮箱 | `admin@example.com` |
| 密码 | `Admin@123456` |

首次启动后，后端会自动创建此账号。可在 `.env` 中修改 `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`。

### 常用命令

```bash
# 查看运行状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 停止（保留数据）
docker compose down

# 完全清理（含数据库）
docker compose down -v
```

---

## API 接口

### 公开接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/articles` | 文章列表（支持 `?q=` 搜索、`?category=`、`?tag=`、分页） |
| GET | `/api/v1/articles/{slug}` | 文章详情（自动累加 view_count） |
| GET | `/api/v1/categories` | 分类列表 |
| GET | `/api/v1/tags` | 标签列表 |
| GET | `/api/v1/articles/{id}/comments` | 已审核评论（树形结构） |
| POST | `/api/v1/articles/{id}/comments` | 提交评论（默认待审核） |
| GET | `/api/v1/search?q=` | 全文搜索 |

### 管理员接口（需 JWT Bearer Token）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录获取 Token |
| GET | `/api/v1/auth/me` | 当前用户信息 |
| POST/PUT/DELETE | `/api/v1/admin/articles` | 文章 CRUD |
| POST | `/api/v1/admin/articles/upload` | 上传 .md 文件创建文章 |
| GET | `/api/v1/admin/articles/{id}/download` | 下载文章 .md 文件 |
| PATCH | `/api/v1/admin/articles/{id}/publish` | 发布 / 撤回文章 |
| POST/PUT/DELETE | `/api/v1/admin/categories` | 分类管理 |
| POST/PUT/DELETE | `/api/v1/admin/tags` | 标签管理 |
| GET | `/api/v1/admin/comments` | 评论列表（`?status=pending/approved/all`） |
| PATCH | `/api/v1/admin/comments/{id}/approve` | 审核评论 |
| POST | `/api/v1/admin/upload/image` | 上传封面图 |

---

## 生产部署

详见 [DEPLOY.md](./DEPLOY.md)，涵盖：

- 阿里云 ECS 环境准备与安全组配置
- 一键部署脚本 `deploy.sh` 的使用
- 手动部署步骤（Docker 安装、环境变量配置）
- HTTPS / Let's Encrypt SSL 证书配置
- 域名绑定
- 数据库自动备份
- 日常运维与故障排除

**快速生产部署：**

```bash
git clone https://github.com/G1011/myblog.git /opt/myblog
cd /opt/myblog
chmod +x deploy.sh && sudo ./deploy.sh
```

---

## 环境变量说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `POSTGRES_DB` | `myblog` | 数据库名 |
| `POSTGRES_USER` | `myblog` | 数据库用户 |
| `POSTGRES_PASSWORD` | `myblog_secret` | 数据库密码（生产环境请修改） |
| `SECRET_KEY` | `change_me_in_production` | JWT 签名密钥（生产环境必须修改） |
| `FIRST_ADMIN_EMAIL` | `admin@example.com` | 初始管理员邮箱 |
| `FIRST_ADMIN_USERNAME` | `admin` | 初始管理员用户名 |
| `FIRST_ADMIN_PASSWORD` | `Admin@123456` | 初始管理员密码（生产环境请修改） |
| `NGINX_PORT` | `80` | Nginx 监听端口 |

> ⚠️ 生产环境请务必修改 `SECRET_KEY`、`POSTGRES_PASSWORD`、`FIRST_ADMIN_PASSWORD`。

---

## License

MIT
