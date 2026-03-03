import client from './client'
import type { APIResponse, Category } from '@/types'

export const categoriesApi = {
  async list(): Promise<Category[]> {
    const res = await client.get<APIResponse<Category[]>>('/categories')
    return res.data.data!
  },

  async create(name: string, description?: string): Promise<Category> {
    const res = await client.post<APIResponse<Category>>('/admin/categories', { name, description })
    return res.data.data!
  },

  async update(id: number, data: { name?: string; description?: string }): Promise<Category> {
    const res = await client.put<APIResponse<Category>>(`/admin/categories/${id}`, data)
    return res.data.data!
  },

  async delete(id: number): Promise<void> {
    await client.delete(`/admin/categories/${id}`)
  },
}
