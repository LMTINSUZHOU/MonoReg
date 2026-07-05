import { defineStore } from 'pinia'
import { getMe, login, type AdminUser } from '../api/auth'

interface AuthState {
  token: string
  user: AdminUser | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('monoreg_token') || '',
    user: null
  }),
  getters: {
    isAuthed: (state) => Boolean(state.token)
  },
  actions: {
    async login(username: string, password: string) {
      const result = await login(username, password)
      this.token = result.access_token
      this.user = result.user
      localStorage.setItem('monoreg_token', result.access_token)
    },
    async fetchMe() {
      if (!this.token) return
      this.user = await getMe()
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('monoreg_token')
    }
  }
})

