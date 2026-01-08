/**
 * 资产选择 Composable
 * 
 * 遵循 .cursorrules 规约:
 * - 复杂交互逻辑必须提取到 @/composables
 * 
 * 提供资产搜索、选择等通用功能
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

/**
 * 资产搜索选择
 */
export function useAssetSearch() {
  const searching = ref(false)
  const availableAssets = ref([])
  
  async function searchAssets(keyword = '', status = 'idle') {
    searching.value = true
    try {
      const params = { 
        status,
        page_size: 50
      }
      
      if (keyword) {
        params.search = keyword
      }
      
      const res = await request.get('/assets/', { params })
      availableAssets.value = res.results || []
      return availableAssets.value
    } catch (error) {
      console.error('搜索资产失败:', error)
      ElMessage.error('搜索资产失败')
      return []
    } finally {
      searching.value = false
    }
  }
  
  async function searchAssetsByUser(userId) {
    searching.value = true
    try {
      const res = await request.get('/assets/', {
        params: { 
          using_user: userId,
          page_size: 100 
        }
      })
      availableAssets.value = res.results || []
      return availableAssets.value
    } catch (error) {
      console.error('获取用户资产失败:', error)
      return []
    } finally {
      searching.value = false
    }
  }
  
  async function searchAssetsByDepartment(departmentId) {
    searching.value = true
    try {
      const res = await request.get('/assets/', {
        params: { 
          using_department: departmentId,
          page_size: 100 
        }
      })
      availableAssets.value = res.results || []
      return availableAssets.value
    } catch (error) {
      console.error('获取部门资产失败:', error)
      return []
    } finally {
      searching.value = false
    }
  }
  
  return {
    searching,
    availableAssets,
    searchAssets,
    searchAssetsByUser,
    searchAssetsByDepartment
  }
}

/**
 * 用户和部门选项
 */
export function useUserDepartmentOptions() {
  const userOptions = ref([])
  const departmentOptions = ref([])
  const locationOptions = ref([])
  
  async function loadUserOptions() {
    try {
      const res = await request.get('/accounts/users/', { params: { page_size: 500 } })
      userOptions.value = res.results || []
    } catch (error) {
      console.error('加载用户列表失败:', error)
    }
  }
  
  async function loadDepartmentOptions() {
    try {
      const res = await request.get('/organizations/departments/tree/')
      departmentOptions.value = processTreeData(res)
    } catch (error) {
      console.error('加载部门列表失败:', error)
    }
  }
  
  async function loadLocationOptions() {
    try {
      const res = await request.get('/organizations/locations/tree/')
      locationOptions.value = processTreeData(res)
    } catch (error) {
      console.error('加载位置列表失败:', error)
    }
  }
  
  // 处理树形数据，添加 displayName
  function processTreeData(data) {
    if (!Array.isArray(data)) return []
    
    return data.map(item => ({
      ...item,
      displayName: item.name,
      children: item.children ? processTreeData(item.children) : undefined
    }))
  }
  
  async function loadAllOptions() {
    await Promise.all([
      loadUserOptions(),
      loadDepartmentOptions(),
      loadLocationOptions()
    ])
  }
  
  return {
    userOptions,
    departmentOptions,
    locationOptions,
    loadUserOptions,
    loadDepartmentOptions,
    loadLocationOptions,
    loadAllOptions
  }
}
