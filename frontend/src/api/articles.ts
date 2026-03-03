import axios from 'axios'
import client from './client'
import type { APIResponse, PaginatedResponse, Article, ArticleSummary } from '@/types'

export interface ArticleListParams {
  page?: number
  size?: number
  category?: string
  tag?: string
  q?: string
}

export interface ArticleCreatePayload {
  title: string
  summary?: string
  content_md: string
  cover_image?: string
  status: string
  category_id?: number | null
  tag_ids: number[]
}

export const articlesApi = {
  async list(params: ArticleListParams = {}): Promise<PaginatedResponse<ArticleSummary>> {
    const res = await client.get<APIResponse<PaginatedResponse<ArticleSummary>>>('/articles', { params })
    return res.data.data!
  },

  async getBySlug(slug: string): Promise<Article> {
    const res = await client.get<APIResponse<Article>>(`/articles/${slug}`)
    return res.data.data!
  },

  // Admin
  async adminList(page = 1, size = 20): Promise<PaginatedResponse<ArticleSummary>> {
    const res = await client.get<APIResponse<PaginatedResponse<ArticleSummary>>>('/admin/articles', {
      params: { page, size },
    })
    return res.data.data!
  },

  async adminGet(id: number): Promise<Article> {
    const res = await client.get<APIResponse<Article>>(`/admin/articles/${id}`)
    return res.data.data!
  },

  async create(data: ArticleCreatePayload): Promise<Article> {
    const res = await client.post<APIResponse<Article>>('/admin/articles', data)
    return res.data.data!
  },

  async update(id: number, data: Partial<ArticleCreatePayload>): Promise<Article> {
    const res = await client.put<APIResponse<Article>>(`/admin/articles/${id}`, data)
    return res.data.data!
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/admin/articles/${id}`)
  },

  async publish(id: number): Promise<ArticleSummary> {
    const res = await client.patch<APIResponse<ArticleSummary>>(`/admin/articles/${id}/publish`)
    return res.data.data!
  },

  async unpublish(id: number): Promise<ArticleSummary> {
    const res = await client.patch<APIResponse<ArticleSummary>>(`/admin/articles/${id}/unpublish`)
    return res.data.data!
  },

  async uploadMd(file: File): Promise<Article> {
    const form = new FormData()
    form.append('file', file)
    const res = await client.post<APIResponse<Article>>('/admin/articles/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data.data!
  },

  async downloadMd(id: number, slug: string): Promise<void> {
    const token = localStorage.getItem('admin_token')
    const response = await axios.get(`/api/v1/admin/articles/${id}/download`, {
      responseType: 'blob',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `${slug}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  },
}
