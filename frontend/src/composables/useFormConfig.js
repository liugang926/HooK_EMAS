/**
 * 动态表单配置服务
 * 
 * 提供统一的表单配置管理，包括：
 * - 获取模块表单配置
 * - 字段配置处理
 * - 表单数据验证
 * - 统一的数据提交
 */

import { ref, reactive, computed } from 'vue'
import request from '@/utils/request'

/**
 * 表单配置 composable
 * @param {string} module - 模块名称，如 'asset', 'consumable'
 * @returns {Object} 表单配置相关方法和状态
 */
export function useFormConfig(module) {
  // 表单配置
  const formConfig = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * 获取表单配置
   * @param {string} mode - 'create' 或 'edit'
   */
  async function loadFormConfig(mode = 'create') {
    loading.value = true
    error.value = null
    
    try {
      const res = await request.get('/system/form/modules/form_config/', {
        params: { module, mode }
      })
      formConfig.value = res.data || res
      return formConfig.value
    } catch (err) {
      error.value = err.message || '加载表单配置失败'
      console.error('加载表单配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取列表字段配置
   */
  async function loadListFields() {
    try {
      const res = await request.get('/system/form/fields/list_fields/', {
        params: { module }
      })
      return res.data || res
    } catch (err) {
      console.error('加载列表字段配置失败:', err)
      throw err
    }
  }
  
  /**
   * 初始化表单数据
   * @param {Object} data - 已有数据（编辑模式）
   * @returns {Object} 初始化后的表单数据
   */
  function initFormData(data = null) {
    if (!formConfig.value) {
      return {}
    }
    
    const formData = {}
    const allFields = getAllFields()
    
    allFields.forEach(field => {
      if (data && data[field.key] !== undefined) {
        // 编辑模式：使用已有数据
        formData[field.key] = data[field.key]
      } else if (field.defaultValue !== undefined && field.defaultValue !== null) {
        // 新增模式：使用默认值
        formData[field.key] = field.defaultValue
      } else {
        // 根据类型设置空值
        formData[field.key] = getEmptyValue(field.type)
      }
    })
    
    return formData
  }
  
  /**
   * 获取所有字段配置
   */
  function getAllFields() {
    if (!formConfig.value) return []
    
    const fields = []
    
    // 收集分组内的字段
    if (formConfig.value.groups) {
      formConfig.value.groups.forEach(group => {
        if (group.fields) {
          fields.push(...group.fields)
        }
      })
    }
    
    // 收集未分组的字段
    if (formConfig.value.ungroupedFields) {
      fields.push(...formConfig.value.ungroupedFields)
    }
    
    return fields
  }
  
  /**
   * 根据字段类型获取空值
   */
  function getEmptyValue(type) {
    switch (type) {
      case 'number':
      case 'decimal':
        return 0
      case 'switch':
      case 'checkbox':
        return false
      case 'multi_select':
        return []
      case 'date':
      case 'datetime':
      case 'reference':
      case 'tree_select':
      case 'cascader':
      case 'image':
      case 'file':
        return null
      default:
        return ''
    }
  }
  
  /**
   * 构建验证规则
   */
  function buildValidationRules() {
    if (!formConfig.value) return {}
    
    const rules = {}
    const allFields = getAllFields()
    
    allFields.forEach(field => {
      if (field.rules && field.rules.length > 0) {
        rules[field.key] = field.rules
      }
    })
    
    return rules
  }
  
  /**
   * 准备提交数据（过滤只读和隐藏字段）
   * @param {Object} formData - 表单数据
   * @param {string} mode - 'create' 或 'edit'
   */
  function prepareSubmitData(formData, mode = 'create') {
    if (!formConfig.value) return formData
    
    const submitData = {}
    const allFields = getAllFields()
    
    allFields.forEach(field => {
      // 跳过只读字段（除非是编辑模式下的非只读字段）
      if (field.readonly) {
        return
      }
      
      // 跳过隐藏字段
      if (field.hidden) {
        return
      }
      
      const value = formData[field.key]
      
      // 跳过空值（可选）
      if (value === null || value === undefined || value === '') {
        // 如果是必填字段，仍然保留
        if (field.required) {
          submitData[field.key] = value
        }
        return
      }
      
      submitData[field.key] = value
    })
    
    return submitData
  }
  
  /**
   * 提交表单数据
   * @param {Object} formData - 表单数据
   * @param {string} mode - 'create' 或 'edit'
   * @param {number|string} id - 编辑模式下的记录ID
   */
  async function submitForm(formData, mode = 'create', id = null) {
    if (!formConfig.value) {
      throw new Error('表单配置未加载')
    }
    
    const apiBase = formConfig.value.apiBase
    const submitData = prepareSubmitData(formData, mode)
    
    try {
      let result
      if (mode === 'create') {
        result = await request.post(apiBase, submitData)
      } else {
        result = await request.put(`${apiBase}${id}/`, submitData)
      }
      return result.data || result
    } catch (err) {
      console.error('提交表单失败:', err)
      throw err
    }
  }
  
  /**
   * 提交表单数据（带文件上传）
   */
  async function submitFormWithFiles(formData, mode = 'create', id = null, fileFields = []) {
    if (!formConfig.value) {
      throw new Error('表单配置未加载')
    }
    
    const apiBase = formConfig.value.apiBase
    const submitData = prepareSubmitData(formData, mode)
    
    // 检查是否有文件需要上传
    const hasFiles = fileFields.some(field => formData[field] instanceof File)
    
    if (hasFiles) {
      // 使用 FormData 上传
      const fd = new FormData()
      
      Object.keys(submitData).forEach(key => {
        const value = submitData[key]
        if (value !== null && value !== undefined) {
          if (value instanceof File) {
            fd.append(key, value)
          } else if (Array.isArray(value)) {
            value.forEach(item => fd.append(key, item))
          } else {
            fd.append(key, value)
          }
        }
      })
      
      // 添加文件字段
      fileFields.forEach(field => {
        if (formData[field] instanceof File) {
          fd.append(field, formData[field])
        }
      })
      
      try {
        let result
        if (mode === 'create') {
          result = await request.post(apiBase, fd, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        } else {
          result = await request.put(`${apiBase}${id}/`, fd, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        }
        return result.data || result
      } catch (err) {
        console.error('提交表单失败:', err)
        throw err
      }
    } else {
      // 普通 JSON 提交
      return submitForm(formData, mode, id)
    }
  }
  
  return {
    // 状态
    formConfig,
    loading,
    error,
    
    // 方法
    loadFormConfig,
    loadListFields,
    initFormData,
    getAllFields,
    buildValidationRules,
    prepareSubmitData,
    submitForm,
    submitFormWithFiles,
  }
}

/**
 * 表单数据管理 composable
 * 用于管理表单数据的响应式状态
 */
export function useFormData() {
  const formData = reactive({})
  const originalData = ref(null)
  const isDirty = computed(() => {
    if (!originalData.value) return false
    return JSON.stringify(formData) !== JSON.stringify(originalData.value)
  })
  
  /**
   * 初始化表单数据
   */
  function init(data = {}) {
    Object.keys(formData).forEach(key => delete formData[key])
    Object.assign(formData, data)
    originalData.value = JSON.parse(JSON.stringify(data))
  }
  
  /**
   * 重置表单数据
   */
  function reset() {
    if (originalData.value) {
      Object.keys(formData).forEach(key => delete formData[key])
      Object.assign(formData, JSON.parse(JSON.stringify(originalData.value)))
    }
  }
  
  /**
   * 清空表单数据
   */
  function clear() {
    Object.keys(formData).forEach(key => delete formData[key])
    originalData.value = null
  }
  
  /**
   * 获取变更的字段
   */
  function getChangedFields() {
    if (!originalData.value) return Object.keys(formData)
    
    const changed = []
    Object.keys(formData).forEach(key => {
      if (JSON.stringify(formData[key]) !== JSON.stringify(originalData.value[key])) {
        changed.push(key)
      }
    })
    return changed
  }
  
  return {
    formData,
    isDirty,
    init,
    reset,
    clear,
    getChangedFields,
  }
}

export default useFormConfig
