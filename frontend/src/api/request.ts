import axios from 'axios'
import { ElMessage } from 'element-plus'

export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
  code?: string
  details?: unknown
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30000
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('monoreg_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const payload = response.data as ApiResponse<unknown>
    if (payload && payload.success === false) {
      ElMessage.error(payload.message || '请求失败')
      return Promise.reject(payload)
    }
    return response
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('monoreg_token')
      window.location.href = '/login'
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await promise
  return response.data.data
}

