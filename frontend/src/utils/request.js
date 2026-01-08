import axios from 'axios'
import { ElMessage } from 'element-plus'

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
    // 从 localStorage 获取 token (与 api/request.js 统一使用 access_token)
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
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回数据部分
    return response.data
  },
  (error) => {
    // 处理错误响应
    let message = '请求失败'
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.error || data.message || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          // 跳转到登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = data.error || '服务器内部错误'
          break
        default:
          message = data.error || data.message || `请求失败: ${status}`
      }
    } else if (error.request) {
      message = '网络错误，请检查网络连接'
    } else {
      message = error.message
    }
    
    // 显示错误消息
    ElMessage.error(message)
    
    return Promise.reject(error)
  }
)

export default request
