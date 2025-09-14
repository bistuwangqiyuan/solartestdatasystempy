import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '@/utils/api'

interface User {
  id: string
  email: string
  full_name?: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/api/v1/auth/login', 
            new URLSearchParams({
              username: email,
              password: password,
            }),
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            }
          )

          const { access_token, user } = response.data
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
          })

          // 设置 axios 默认 header
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        } catch (error) {
          throw error
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
        
        // 清除 axios 默认 header
        delete api.defaults.headers.common['Authorization']
        
        // 可选：调用后端登出接口
        api.post('/api/v1/auth/logout').catch(() => {})
      },

      checkAuth: () => {
        const state = get()
        if (state.token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
          
          // 验证 token 是否有效
          api.get('/api/v1/auth/me')
            .then(response => {
              set({ user: response.data })
            })
            .catch(() => {
              // Token 无效，清除认证状态
              get().logout()
            })
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)