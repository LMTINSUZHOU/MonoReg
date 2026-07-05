import { request, unwrap } from './request'

export interface AdminUser {
  id: number
  username: string
  email: string
  role: string
  status: string
}

export function login(username: string, password: string) {
  return unwrap<{ access_token: string; token_type: string; user: AdminUser }>(
    request.post('/api/auth/login', { username, password })
  )
}

export function getMe() {
  return unwrap<AdminUser>(request.get('/api/auth/me'))
}

