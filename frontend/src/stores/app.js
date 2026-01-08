import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'
import request from '@/utils/request'

export const useAppStore = defineStore('app', () => {
  // 侧边栏状态
  const sidebarCollapsed = ref(false)
  
  // 当前公司
  const currentCompany = ref(null)
  
  // 公司列表
  const companies = ref([])
  
  // 当前公司ID (computed for easier access)
  const currentCompanyId = computed(() => currentCompany.value?.id || null)
  
  // 从localStorage加载保存的公司
  const savedCompanyId = localStorage.getItem('currentCompanyId')
  const savedCompanyData = localStorage.getItem('currentCompanyData')
  if (savedCompanyData) {
    try {
      currentCompany.value = JSON.parse(savedCompanyData)
    } catch (e) {
      console.error('加载保存的公司数据失败:', e)
    }
  }
  
  // 系统配置
  const systemConfig = ref({
    name: '钩子资产',
    logo: '',
    primaryColor: '#3b82f6',
    theme: 'light',
    copyright: '© 2026 钩子资产 版权所有',
    favicon: ''
  })
  
  // 从本地存储加载配置
  const savedConfig = localStorage.getItem('systemConfig')
  if (savedConfig) {
    try {
      const parsed = JSON.parse(savedConfig)
      systemConfig.value = { ...systemConfig.value, ...parsed }
    } catch (e) {
      console.error('加载系统配置失败:', e)
    }
  }
  
  // 监听配置变化，保存到本地
  watch(systemConfig, (newConfig) => {
    localStorage.setItem('systemConfig', JSON.stringify(newConfig))
    // 应用主题色
    applyTheme(newConfig)
  }, { deep: true })
  
  // 应用主题
  function applyTheme(config) {
    const root = document.documentElement
    const primaryColor = config.primaryColor || '#3b82f6'
    
    // 设置主题色
    root.style.setProperty('--el-color-primary', primaryColor)
    
    // 计算并设置主题色的各种变体
    const dark2Color = mixColor(primaryColor, '#000000', 0.2)
    const light3Color = mixColor(primaryColor, '#ffffff', 0.3)
    const light5Color = mixColor(primaryColor, '#ffffff', 0.5)
    const light7Color = mixColor(primaryColor, '#ffffff', 0.7)
    const light8Color = mixColor(primaryColor, '#ffffff', 0.8)
    const light9Color = mixColor(primaryColor, '#ffffff', 0.9)
    
    root.style.setProperty('--el-color-primary-light-3', light3Color)
    root.style.setProperty('--el-color-primary-light-5', light5Color)
    root.style.setProperty('--el-color-primary-light-7', light7Color)
    root.style.setProperty('--el-color-primary-light-8', light8Color)
    root.style.setProperty('--el-color-primary-light-9', light9Color)
    root.style.setProperty('--el-color-primary-dark-2', dark2Color)
    
    // 动态创建/更新样式标签以强制更新侧边栏激活样式
    let dynamicStyle = document.getElementById('dynamic-theme-style')
    if (!dynamicStyle) {
      dynamicStyle = document.createElement('style')
      dynamicStyle.id = 'dynamic-theme-style'
      document.head.appendChild(dynamicStyle)
    }
    
    // 使用动态样式覆盖侧边栏激活菜单项的背景
    dynamicStyle.textContent = `
      .sidebar-menu .el-menu-item.is-active,
      .sidebar-menu .el-menu--inline .el-menu-item.is-active {
        background: linear-gradient(90deg, ${primaryColor} 0%, ${dark2Color} 100%) !important;
        color: #fff !important;
      }
      .el-button--primary {
        --el-button-bg-color: ${primaryColor};
        --el-button-border-color: ${primaryColor};
        --el-button-hover-bg-color: ${light3Color};
        --el-button-hover-border-color: ${light3Color};
        --el-button-active-bg-color: ${dark2Color};
        --el-button-active-border-color: ${dark2Color};
      }
    `
    
    // 应用深色/浅色主题
    if (config.theme === 'dark') {
      document.body.classList.add('dark-theme')
      document.documentElement.classList.add('dark')
    } else {
      document.body.classList.remove('dark-theme')
      document.documentElement.classList.remove('dark')
    }
    
    // 更新页面标题
    if (config.name) {
      document.title = config.name
    }
    
    // 更新favicon
    if (config.favicon) {
      let link = document.querySelector("link[rel*='icon']")
      if (!link) {
        link = document.createElement('link')
        link.type = 'image/x-icon'
        link.rel = 'shortcut icon'
        document.getElementsByTagName('head')[0].appendChild(link)
      }
      link.href = config.favicon
    }
  }
  
  // 颜色混合函数 - 更准确的颜色计算
  function mixColor(color1, color2, weight) {
    const d2h = (d) => d.toString(16).padStart(2, '0')
    const h2d = (h) => parseInt(h, 16)
    
    const c1 = color1.replace('#', '')
    const c2 = color2.replace('#', '')
    
    let color = '#'
    for (let i = 0; i <= 2; i++) {
      const v1 = h2d(c1.substring(i * 2, i * 2 + 2))
      const v2 = h2d(c2.substring(i * 2, i * 2 + 2))
      const val = Math.round(v1 * (1 - weight) + v2 * weight)
      color += d2h(Math.min(255, Math.max(0, val)))
    }
    return color
  }
  
  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  // 设置当前公司
  function setCurrentCompany(company) {
    currentCompany.value = company
    // 保存到localStorage
    if (company) {
      localStorage.setItem('currentCompanyId', company.id)
      localStorage.setItem('currentCompanyData', JSON.stringify(company))
    } else {
      localStorage.removeItem('currentCompanyId')
      localStorage.removeItem('currentCompanyData')
    }
  }
  
  // 加载公司列表
  async function loadCompanies() {
    try {
      const res = await request.get('/organizations/companies/')
      companies.value = res.results || res || []
      
      // 如果没有当前公司，或当前公司不在列表中，自动选择第一个
      if (companies.value.length > 0) {
        const savedId = localStorage.getItem('currentCompanyId')
        const savedCompany = savedId 
          ? companies.value.find(c => c.id === parseInt(savedId)) 
          : null
        
        if (savedCompany) {
          currentCompany.value = savedCompany
        } else if (!currentCompany.value) {
          setCurrentCompany(companies.value[0])
        }
      }
      
      return companies.value
    } catch (error) {
      console.error('加载公司列表失败:', error)
      return []
    }
  }
  
  // 更新系统配置
  function updateSystemConfig(config) {
    systemConfig.value = { ...systemConfig.value, ...config }
  }
  
  // 加载系统配置（从后端）
  async function loadSystemConfig() {
    try {
      const res = await request.get('/system/config/')
      if (res && res.config) {
        systemConfig.value = { ...systemConfig.value, ...res.config }
      }
    } catch (error) {
      console.error('加载系统配置失败:', error)
    }
  }
  
  // 保存系统配置（到后端）
  async function saveSystemConfig(config) {
    try {
      await request.post('/system/config/', { config })
      systemConfig.value = { ...systemConfig.value, ...config }
      return true
    } catch (error) {
      console.error('保存系统配置失败:', error)
      return false
    }
  }
  
  // 初始化时应用主题
  applyTheme(systemConfig.value)
  
  return {
    sidebarCollapsed,
    currentCompany,
    currentCompanyId,
    companies,
    systemConfig,
    toggleSidebar,
    setCurrentCompany,
    loadCompanies,
    updateSystemConfig,
    loadSystemConfig,
    saveSystemConfig,
    applyTheme
  }
})
