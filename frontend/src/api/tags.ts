import client from './client'
import type { APIResponse, Tag } from '@/types'

export const tagsApi = {
  async list(): Promise<Tag[]> {
    const res = await client.get<APIResponse<Tag[]>>('/tags')
    return res.data.data!
  },

  async create(name: string): Promise<Tag> {
    const res = await client.post<APIResponse<Tag>>('/admin/tags', { name })
    return res.data.data!
  },

  async update(id: number, name: string): Promise<Tag> {
    const res = await client.put<APIResponse<Tag>>(`/admin/tags/${id}`, { name })
    return res.data.data!
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/admin/tags/${id}`)
  },
}
