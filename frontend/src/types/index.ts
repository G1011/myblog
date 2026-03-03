export interface APIResponse<T> {
  code: number
  message: string
  data: T | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface TagBrief {
  id: number
  name: string
  slug: string
}

export interface CategoryBrief {
  id: number
  name: string
  slug: string
}

export interface AuthorBrief {
  id: number
  username: string
}

export interface ArticleSummary {
  id: number
  title: string
  slug: string
  summary: string | null
  cover_image: string | null
  status: string
  view_count: number
  published_at: string | null
  created_at: string
  author: AuthorBrief | null
  category: CategoryBrief | null
  tags: TagBrief[]
}

export interface Article extends ArticleSummary {
  content_md: string
}

export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  article_count: number
  created_at: string
}

export interface Tag {
  id: number
  name: string
  slug: string
  article_count: number
}

export interface Comment {
  id: number
  article_id: number
  parent_id: number | null
  author_name: string
  body: string
  is_approved: boolean
  created_at: string
  replies: Comment[]
}

export interface AdminUser {
  id: number
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface Stats {
  total_articles: number
  published_articles: number
  draft_articles: number
  total_views: number
  pending_comments: number
}
