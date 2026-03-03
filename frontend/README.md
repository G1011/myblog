# MyBlog Frontend

基于 **Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS** 构建的博客前端，极简黑白风格，支持浅色/深色双主题，含公开博客展示和管理员后台两套界面。

---

## 架构说明

```
src/
├── main.ts                    # 应用入口，挂载 Vue + Pinia + Router
├── App.vue                    # 根组件（主题 class 应用）
├── types/
│   └── index.ts               # 与后端 schema 对应的 TypeScript 接口
├── api/
│   ├── client.ts              # Axios 实例：请求拦截器（附 JWT）+ 401 自动跳转
│   ├── articles.ts            # 文章 API 封装
│   ├── categories.ts          # 分类 API 封装
│   ├── tags.ts                # 标签 API 封装
│   ├── comments.ts            # 评论 API 封装
│   ├── search.ts              # 搜索 API 封装
│   └── auth.ts                # 认证 API 封装
├── stores/
│   ├── auth.ts                # 管理员 token + 用户信息 + login/logout
│   └── theme.ts               # 深色/浅色切换 → <html class="dark">
├── router/
│   └── index.ts               # 路由表 + beforeEach 路由守卫
├── composables/
│   ├── useMarkdown.ts         # Markdown → HTML（marked + highlight.js）
│   ├── usePagination.ts       # 分页状态管理（currentPage / totalPages / goToPage）
│   └── useSearch.ts           # 防抖搜索（debounce 300ms）
├── layouts/
│   ├── PublicLayout.vue       # 公开页面布局（Header + Footer + RouterView）
│   └── AdminLayout.vue        # 后台布局（侧边栏 + 内容区）
├── components/
│   ├── common/
│   │   ├── TheHeader.vue      # 顶栏（导航、主题切换、搜索入口）
│   │   ├── TheFooter.vue      # 底栏
│   │   ├── ThemeToggle.vue    # 深色/浅色切换按钮
│   │   └── Pagination.vue     # 通用分页组件
│   ├── article/
│   │   ├── ArticleCard.vue    # 文章列表卡片
│   │   └── ArticleContent.vue # Markdown 渲染（含代码高亮）
│   ├── comment/
│   │   ├── CommentList.vue    # 评论列表（树形展示）
│   │   ├── CommentItem.vue    # 单条评论 + 回复
│   │   └── CommentForm.vue    # 游客留言表单
│   └── admin/
│       ├── AdminSidebar.vue   # 后台侧边导航
│       ├── ArticleEditor.vue  # Markdown 双栏编辑器（左编辑 + 右预览）
│       └── ConfirmDialog.vue  # 危险操作确认弹窗
└── views/
    ├── public/
    │   ├── AboutView.vue      # 首页 / About（个人介绍）
    │   ├── BlogView.vue       # 博客列表（分类过滤、标签筛选、分页）
    │   ├── ArticleDetailView.vue  # 文章详情 + 评论区
    │   ├── CategoryView.vue   # 按分类浏览文章
    │   ├── TagView.vue        # 按标签浏览文章
    │   ├── SearchView.vue     # 全文搜索结果
    │   └── NotFoundView.vue   # 404 页面
    └── admin/
        ├── LoginView.vue      # 管理员登录
        ├── DashboardView.vue  # 仪表盘（统计概览）
        ├── ArticlesView.vue   # 文章列表（含发布/撤回/删除）
        ├── ArticleEditView.vue # 文章创建/编辑（双栏 Markdown 编辑器）
        ├── CategoriesView.vue # 分类管理（增删改）
        ├── TagsView.vue       # 标签管理（增删改）
        └── CommentsView.vue   # 评论审核（待审核/已通过/删除）
```

### 设计模式

| 模式 | 说明 |
|------|------|
| **Composition API** | 所有组件使用 `<script setup>` + Composition API，逻辑清晰内聚 |
| **Composables** | 可复用逻辑（分页、搜索、Markdown 渲染）提取为独立 composables |
| **Pinia Store** | 全局状态（认证、主题）通过 Pinia 管理，支持持久化到 localStorage |
| **API 层分离** | 所有 HTTP 请求封装在 `src/api/`，视图层不直接调用 axios |
| **Mock Fallback** | 后端不可用时自动降级到 Mock 数据（BlogView），保证开发体验 |
| **路由守卫** | `beforeEach` 检查 token，未登录访问 `/admin/*` 自动跳转登录页 |

---

## 路由结构

```
/                        → PublicLayout
  /                      → AboutView（个人介绍首页）
  /blog                  → BlogView（文章列表，支持 ?category= 过滤）
  /blog/:slug            → ArticleDetailView（文章详情 + 评论）
  /category/:slug        → CategoryView
  /tag/:slug             → TagView
  /search                → SearchView

/admin/login             → LoginView（独立页面，无 Layout）
/admin                   → AdminLayout（需登录）
  /admin/                → DashboardView
  /admin/articles        → ArticlesView
  /admin/articles/new    → ArticleEditView（创建模式）
  /admin/articles/:id/edit → ArticleEditView（编辑模式）
  /admin/categories      → CategoriesView
  /admin/tags            → TagsView
  /admin/comments        → CommentsView

/*                       → NotFoundView（404）
```

---

## 环境要求

- Node.js 18+
- npm / yarn / pnpm

---

## 本地开发启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置代理（可选）

开发时 Vite 自动将以下路径代理到后端（`http://localhost:8000`）：

| 路径前缀 | 目标 |
|----------|------|
| `/api` | `http://localhost:8000` |
| `/uploads` | `http://localhost:8000` |
| `/health` | `http://localhost:8000` |

无需额外配置，修改 `vite.config.ts` 中的 `target` 可更改后端地址。

### 3. 启动开发服务器

```bash
npm run dev
```

默认访问地址：http://localhost:5173

> 若后端未启动，BlogView 会自动回退到 Mock 数据展示。

### 4. 类型检查

```bash
npm run type-check
```

### 5. 生产构建

```bash
npm run build
# 构建产物输出到 dist/ 目录
```

---

## Docker 部署

```bash
# 在项目根目录执行
cd ..
docker compose up --build
```

前端 Dockerfile 采用多阶段构建：`node` 镜像构建 → `nginx:alpine` 服务静态文件。

---

## 功能说明

### 公开访问

#### 首页（About）
- 个人介绍页面，展示博主信息

#### 博客列表
- 文章卡片列表，展示标题、摘要、发布时间、分类、标签
- 支持按分类过滤（`?category=tech` / `?category=life`）
- 支持按标签筛选（点击标签名）
- 分页浏览

#### 文章详情
- Markdown 渲染，支持代码块语法高亮（highlight.js）
- 展示文章元信息（作者、发布时间、分类、标签）
- 游客评论区：提交留言（需管理员审核后显示）

#### 分类 / 标签页
- 展示属于指定分类或标签的文章列表

#### 全文搜索
- 关键词搜索（防抖 300ms）
- 调用后端 PostgreSQL 全文索引

---

### 管理员后台（需登录）

#### 登录
- 邮箱 + 密码登录（默认：`admin@example.com` / `Admin@123456`）
- 登录成功后 JWT 存入 `localStorage`，自动附加到后续请求

#### 仪表盘
- 统计概览：总文章数、已发布、草稿、总浏览量、待审评论数

#### 文章管理
- 文章列表：显示状态（草稿/已发布）、浏览量、操作按钮
- 一键发布 / 撤回为草稿
- 删除文章（二次确认）
- 新建/编辑文章（跳转编辑器）

#### 文章编辑器
- 左侧 Markdown 编辑，右侧实时 HTML 预览（双栏布局）
- 支持设置标题、摘要、分类、标签、封面图（上传）
- 保存草稿 / 直接发布

#### 分类管理
- 创建分类（支持自定义 slug）、修改、删除

#### 标签管理
- 创建标签、修改、删除

#### 评论审核
- 分 `待审核` / `已通过` / `全部` 三个标签页
- 一键审核通过或删除评论

---

## 主题说明

- 使用 Tailwind CSS `darkMode: 'class'` 方案
- 主题状态持久化到 `localStorage`（`theme` key）
- 切换时通过 `useThemeStore` 在 `<html>` 上添加/移除 `dark` class

---

## API 层说明

所有 API 模块均基于 `src/api/client.ts` 封装的 Axios 实例：

- **请求拦截器**：自动从 `localStorage` 读取 `admin_token` 并附加 `Authorization: Bearer` 头
- **响应拦截器**：统一解包 `APIResponse<T>` 的 `data` 字段；HTTP 401 自动跳转 `/admin/login`
- **错误处理**：非 2xx 响应抛出含后端 `message` 的 Error，由各视图层 `try/catch` 处理

---

## 主要依赖

| 包 | 版本 | 用途 |
|----|------|------|
| vue | ^3.5 | 核心框架 |
| vue-router | ^4.5 | 路由管理 |
| pinia | ^2.3 | 全局状态管理 |
| axios | ^1.7 | HTTP 客户端 |
| marked | ^15.0 | Markdown 解析 |
| highlight.js | ^11.10 | 代码高亮 |
| tailwindcss | ^3.4 | 原子化 CSS |
| @tailwindcss/typography | ^0.5 | Markdown 排版样式 |
| vite | ^6.0 | 构建工具 |
| typescript | ^5.7 | 类型系统 |
