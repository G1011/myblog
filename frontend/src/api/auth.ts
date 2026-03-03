import client from './client'
import type { APIResponse, TokenResponse, AdminUser } from '@/types'

export const authApi = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await client.post<APIResponse<TokenResponse>>('/auth/login', { email, password })
    return res.data.data!
  },

  async getMe(): Promise<AdminUser> {
    const res = await client.get<APIResponse<AdminUser>>('/auth/me')
    return res.data.data!
  },
}
