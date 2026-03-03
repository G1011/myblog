import client from './client'
import type { APIResponse, Stats } from '@/types'

export const statsApi = {
  async get(): Promise<Stats> {
    const res = await client.get<APIResponse<Stats>>('/admin/stats')
    return res.data.data!
  },
}
