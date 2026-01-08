import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getUserInfo, logout } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const userInfo = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const displayName = computed(() => userInfo.value?.display_name || userInfo.value?.username || '')
  const avatar = computed(() => userInfo.value?.avatar || '')
  
  // 登录
  async function doLogin(credentials) {
    try {
      const res = await login(credentials)
      token.value = res.access
      refreshToken.value = res.refresh
      userInfo.value = res.user
      
      localStorage.setItem('access_token', res.access)
      localStorage.setItem('refresh_token', res.refresh)
      
      return res
    } catch (error) {
      throw error
    }
  }
  
  // 检查认证状态
  async function checkAuth() {
    if (!token.value) return false
    
    try {
      const res = await getUserInfo()
      userInfo.value = res
      return true
    } catch (error) {
      // Token 过期或无效
      clearAuth()
      return false
    }
  }
  
  // 登出
  async function doLogout() {
    try {
      await logout()
    } finally {
      clearAuth()
      router.push({ name: 'Login' })
    }
  }
  
  // 清除认证信息
  function clearAuth() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
  
  // 更新 Token
  function updateToken(newToken, newRefreshToken) {
    token.value = newToken
    if (newRefreshToken) {
      refreshToken.value = newRefreshToken
    }
    localStorage.setItem('access_token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refresh_token', newRefreshToken)
    }
  }
  
  // 直接设置用户信息（用于登录后从响应中获取用户信息，避免额外的API调用）
  function setUserInfo(user) {
    userInfo.value = user
  }
  
  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    displayName,
    avatar,
    doLogin,
    checkAuth,
    doLogout,
    clearAuth,
    updateToken,
    setUserInfo
  }
})
