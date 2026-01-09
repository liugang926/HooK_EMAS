/**
 * Dynamic Module Composable
 * 
 * Universal composable that combines all module-related functionality:
 * - Form configuration
 * - Field definitions
 * - List fields
 * - Code generation
 * - CRUD operations
 * 
 * Usage:
 *   const {
 *     moduleConfig,
 *     moduleLabel,
 *     fields,
 *     listFields,
 *     loading,
 *     loadModuleConfig,
 *     loadListFields,
 *     fetchData,
 *     createRecord,
 *     updateRecord,
 *     deleteRecord,
 *     bulkDelete,
 *     generateCode
 *   } = useDynamicModule('asset')
 */

import { ref, computed } from 'vue'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'
import { useCodeRule } from './useCodeRule'

/**
 * Module Configuration Registry (frontend mirror of backend MODULE_REGISTRY)
 */
const MODULE_CONFIG = {
  asset: {
    label: '资产',
    apiBase: '/assets/list/',
    supportsCodeRule: true,
  },
  supply: {
    label: '办公用品',
    apiBase: '/consumables/list/',
    supportsCodeRule: true,
  },
  consumable: {
    label: '办公用品',
    apiBase: '/consumables/list/',
    supportsCodeRule: true,
  },
  user: {
    label: '用户',
    apiBase: '/auth/users/',
    supportsCodeRule: false,
  },
  department: {
    label: '部门',
    apiBase: '/organizations/departments/',
    supportsCodeRule: false,
    treeMode: true,
  },
  location: {
    label: '存放位置',
    apiBase: '/organizations/locations/',
    supportsCodeRule: false,
    treeMode: true,
  },
  company: {
    label: '公司',
    apiBase: '/organizations/companies/',
    supportsCodeRule: false,
  },
  supplier: {
    label: '供应商',
    apiBase: '/procurement/suppliers/',
    supportsCodeRule: false,
  },
  purchase_order: {
    label: '采购订单',
    apiBase: '/procurement/orders/',
    supportsCodeRule: true,
  },
}

/**
 * Dynamic Module Composable
 * @param {string} moduleName - Module identifier (e.g., 'asset', 'supply', 'user')
 * @param {string} customApiBase - Optional custom API base path
 * @returns {Object} Module management methods and state
 */
export function useDynamicModule(moduleName, customApiBase = null) {
  const appStore = useAppStore()
  
  // Get module config
  const localConfig = MODULE_CONFIG[moduleName] || {
    label: moduleName,
    apiBase: `/${moduleName}/`,
    supportsCodeRule: false,
  }
  
  // State
  const loading = ref(false)
  const moduleConfig = ref(null)
  const fields = ref([])
  const listFields = ref([])
  
  // API base path
  const apiBase = computed(() => {
    return customApiBase || localConfig.apiBase
  })
  
  // Module label
  const moduleLabel = computed(() => {
    return moduleConfig.value?.moduleLabel || localConfig.label
  })
  
  // Code rule support
  const codeRuleComposable = localConfig.supportsCodeRule ? useCodeRule(moduleName) : null
  
  /**
   * Load module configuration from backend
   */
  async function loadModuleConfig(mode = 'create') {
    loading.value = true
    try {
      const res = await request.get('/system/form/modules/form_config/', {
        params: { module: moduleName, mode }
      })
      moduleConfig.value = res
      return moduleConfig.value
    } catch (error) {
      console.warn('Module config not found, using defaults')
      moduleConfig.value = {
        module: moduleName,
        moduleLabel: localConfig.label,
        apiBase: apiBase.value,
        dialogWidth: '900px',
        labelWidth: '100px',
        permissions: {
          create: true,
          edit: true,
          delete: true,
          import: true,
          export: true,
        },
        groups: [],
        ungroupedFields: [],
      }
      return moduleConfig.value
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Load field definitions
   */
  async function loadFields(mode = 'create') {
    try {
      const res = await request.get('/system/form/fields/', {
        params: { module: moduleName }
      })
      fields.value = res.results || res || []
      return fields.value
    } catch (error) {
      console.error('Failed to load fields:', error)
      fields.value = []
      return []
    }
  }
  
  /**
   * Load list display fields
   */
  async function loadListFields() {
    try {
      // Try to get from module form config endpoint
      const res = await request.get('/system/form/fields/list_fields/', {
        params: { module: moduleName }
      })
      listFields.value = res || []
      return listFields.value
    } catch (error) {
      // Fallback: filter fields that should show in list
      console.warn('List fields endpoint not found, using field definitions')
      if (fields.value.length === 0) {
        await loadFields()
      }
      listFields.value = fields.value
        .filter(f => f.show_in_list)
        .map(f => ({
          key: f.field_key,
          label: f.field_name,
          type: f.field_type,
          width: f.list_width,
          sortable: f.list_sortable,
          searchable: f.list_searchable,
          options: f.options,
          showInList: f.show_in_list,
        }))
      return listFields.value
    }
  }
  
  /**
   * Fetch data with pagination and filters
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Paginated data
   */
  async function fetchData(params = {}) {
    loading.value = true
    try {
      const res = await request.get(apiBase.value, { params })
      return res
    } catch (error) {
      console.error('Failed to fetch data:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Fetch single record
   * @param {number|string} id - Record ID
   * @returns {Promise<Object>} Record data
   */
  async function fetchRecord(id) {
    loading.value = true
    try {
      const res = await request.get(`${apiBase.value}${id}/`)
      return res
    } catch (error) {
      console.error('Failed to fetch record:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Create new record
   * @param {Object} data - Record data
   * @returns {Promise<Object>} Created record
   */
  async function createRecord(data) {
    loading.value = true
    try {
      const res = await request.post(apiBase.value, data)
      return res
    } catch (error) {
      console.error('Failed to create record:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update existing record
   * @param {number|string} id - Record ID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>} Updated record
   */
  async function updateRecord(id, data) {
    loading.value = true
    try {
      const res = await request.put(`${apiBase.value}${id}/`, data)
      return res
    } catch (error) {
      console.error('Failed to update record:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Partially update record
   * @param {number|string} id - Record ID
   * @param {Object} data - Partial data
   * @returns {Promise<Object>} Updated record
   */
  async function patchRecord(id, data) {
    loading.value = true
    try {
      const res = await request.patch(`${apiBase.value}${id}/`, data)
      return res
    } catch (error) {
      console.error('Failed to patch record:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Delete record
   * @param {number|string} id - Record ID
   * @returns {Promise<void>}
   */
  async function deleteRecord(id) {
    loading.value = true
    try {
      await request.delete(`${apiBase.value}${id}/`)
    } catch (error) {
      console.error('Failed to delete record:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Bulk delete records
   * @param {Array<number|string>} ids - Record IDs
   * @returns {Promise<Object>} Result with deleted count
   */
  async function bulkDelete(ids) {
    loading.value = true
    try {
      const res = await request.post(`${apiBase.value}bulk_delete/`, { ids })
      return res
    } catch (error) {
      // Fallback: delete one by one
      console.warn('Bulk delete not supported, falling back to individual deletes')
      for (const id of ids) {
        await request.delete(`${apiBase.value}${id}/`)
      }
      return { deleted: ids.length }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Bulk create records
   * @param {Array<Object>} items - Record data array
   * @returns {Promise<Array>} Created records
   */
  async function bulkCreate(items) {
    loading.value = true
    try {
      const res = await request.post(`${apiBase.value}bulk_create/`, { items })
      return res
    } catch (error) {
      console.error('Failed to bulk create:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Generate code (if module supports it)
   * @returns {Promise<string>} Generated code
   */
  async function generateCode() {
    if (!localConfig.supportsCodeRule || !codeRuleComposable) {
      throw new Error(`Module ${moduleName} does not support code generation`)
    }
    return codeRuleComposable.generateCode()
  }
  
  /**
   * Export data
   * @param {Object} params - Export parameters
   * @returns {Promise<Blob>} Export file
   */
  async function exportData(params = {}) {
    loading.value = true
    try {
      const res = await request.get(`${apiBase.value}export/`, {
        params,
        responseType: 'blob'
      })
      return res
    } catch (error) {
      console.error('Failed to export data:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Import data
   * @param {FormData} formData - Import file data
   * @returns {Promise<Object>} Import result
   */
  async function importData(formData) {
    loading.value = true
    try {
      const res = await request.post(`${apiBase.value}import/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return res
    } catch (error) {
      console.error('Failed to import data:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  return {
    // State
    loading,
    moduleConfig,
    moduleLabel,
    fields,
    listFields,
    apiBase,
    
    // Config methods
    loadModuleConfig,
    loadFields,
    loadListFields,
    
    // CRUD methods
    fetchData,
    fetchRecord,
    createRecord,
    updateRecord,
    patchRecord,
    deleteRecord,
    
    // Bulk operations
    bulkCreate,
    bulkDelete,
    
    // Code generation (if supported)
    generateCode: localConfig.supportsCodeRule ? generateCode : undefined,
    codeRule: codeRuleComposable?.codeRule,
    loadCodeRule: codeRuleComposable?.loadCodeRule,
    saveCodeRule: codeRuleComposable?.saveCodeRule,
    
    // Import/Export
    exportData,
    importData,
  }
}

export default useDynamicModule
