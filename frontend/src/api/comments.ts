import client from './client'
import type { APIResponse, PaginatedResponse, Comment } from '@/types'

export const commentsApi = {
  async list(articleId: number): Promise<Comment[]> {
    const res = await client.get<APIResponse<Comment[]>>(`/articles/${articleId}/comments`)
    return res.data.data!
  },

  async submit(articleId: number, data: {
    author_name: string
    author_email: string
    body: string
    parent_id?: number
  }): Promise<Comment> {
    const res = await client.post<APIResponse<Comment>>(`/articles/${articleId}/comments`, data)
    return res.data.data!
  },

  async adminList(params: { status?: string; page?: number; size?: number } = {}): Promise<PaginatedResponse<Comment>> {
    const res = await client.get<APIResponse<PaginatedResponse<Comment>>>('/admin/comments', { params })
    return res.data.data!
  },

  async approve(id: number): Promise<Comment> {
    const res = await client.patch<APIResponse<Comment>>(`/admin/comments/${id}/approve`)
    return res.data.data!
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/admin/comments/${id}`)
  },
}
