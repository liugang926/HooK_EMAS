import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// API paths that should NOT have automatic company filtering
const excludeCompanyFilterPaths = [
  '/auth/',
  '/organizations/companies',
  '/system/config',
  '/sso/'
]

// Check if path should be excluded from company filtering
function shouldExcludeCompanyFilter(url) {
  return excludeCompanyFilterPaths.some(path => url.includes(path))
}

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Auto-add company filter for multi-company data isolation
    const currentCompanyId = localStorage.getItem('currentCompanyId')
    if (currentCompanyId && !shouldExcludeCompanyFilter(config.url)) {
      // For GET requests, add to query params
      if (config.method === 'get' && !config.params?.company) {
        config.params = { ...config.params, company: currentCompanyId }
      }
      // For POST/PUT/PATCH requests, add to request body
      if (['post', 'put', 'patch'].includes(config.method)) {
        if (config.data && typeof config.data === 'object' && !config.data.company) {
          config.data = { ...config.data, company: currentCompanyId }
        }
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // Token 过期，尝试刷新
          const userStore = useUserStore()
          const refreshToken = localStorage.getItem('refresh_token')
          
          if (refreshToken && !error.config._retry) {
            error.config._retry = true
            
            try {
              const res = await axios.post('/api/auth/refresh/', {
                refresh: refreshToken
              })
              
              userStore.updateToken(res.data.access)
              error.config.headers.Authorization = `Bearer ${res.data.access}`
              return request(error.config)
            } catch (refreshError) {
              userStore.clearAuth()
              router.push({ name: 'Login' })
              ElMessage.error('登录已过期，请重新登录')
            }
          } else {
            userStore.clearAuth()
            router.push({ name: 'Login' })
            ElMessage.error('登录已过期，请重新登录')
          }
          break
          
        case 403:
          ElMessage.error('没有权限进行此操作')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
          
        default:
          const message = response.data?.detail || response.data?.error || '请求失败'
          ElMessage.error(message)
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default request
