/**
 * Code Rule Composable
 * 
 * Provides functionality for managing code generation rules and generating codes
 * for any module that supports automatic code generation.
 * 
 * Usage:
 *   const { codeRule, loading, loadCodeRule, saveCodeRule, generateCode } = useCodeRule('asset')
 */

import { ref, reactive, computed } from 'vue'
import request from '@/api/request'
import { useAppStore } from '@/stores/app'

/**
 * Code Rule Composable
 * @param {string} moduleName - Module name (e.g., 'asset', 'supply', 'purchase_order')
 * @returns {Object} Code rule methods and state
 */
export function useCodeRule(moduleName) {
  const appStore = useAppStore()
  
  // State
  const loading = ref(false)
  const codeRule = reactive({
    prefix: '',
    dateFormat: 'YYYYMMDD',
    serialLength: 4,
    separator: '',
    resetCycle: 'daily'
  })
  
  // Map module name to code rule type
  const codeRuleTypeMap = {
    asset: 'asset_code',
    supply: 'supply_code',
    purchase_order: 'purchase_order_code',
    consumable: 'supply_code',
  }
  
  // Default prefixes by module
  const defaultPrefixMap = {
    asset: 'ZC',
    supply: 'BG',
    consumable: 'BG',
    purchase_order: 'PO',
  }
  
  /**
   * Get code rule type for the module
   */
  const codeRuleType = computed(() => {
    return codeRuleTypeMap[moduleName] || `${moduleName}_code`
  })
  
  /**
   * Get default prefix for the module
   */
  const defaultPrefix = computed(() => {
    return defaultPrefixMap[moduleName] || 'CODE'
  })
  
  /**
   * Computed example code based on current rule
   */
  const codeExample = computed(() => {
    const date = new Date()
    let dateStr = ''
    
    if (codeRule.dateFormat === 'YYYY') {
      dateStr = date.getFullYear().toString()
    } else if (codeRule.dateFormat === 'YYYYMM') {
      dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}`
    } else {
      dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
    }
    
    const serial = '1'.padStart(codeRule.serialLength, '0')
    const sep = codeRule.separator || ''
    
    return `${codeRule.prefix}${sep}${dateStr}${sep}${serial}`
  })
  
  /**
   * Load code rule from backend
   */
  async function loadCodeRule() {
    loading.value = true
    try {
      const res = await request.get(`/system/code-rules/by-code/${codeRuleType.value}/`, {
        params: { company: appStore.currentCompany?.id }
      })
      
      if (res) {
        codeRule.prefix = res.prefix || defaultPrefix.value
        codeRule.dateFormat = res.date_format || 'YYYYMMDD'
        codeRule.serialLength = res.serial_length || 4
        codeRule.separator = res.separator || ''
        codeRule.resetCycle = res.reset_cycle || 'daily'
      }
    } catch (error) {
      // Use defaults if rule not found
      console.log('Code rule not found, using defaults')
      codeRule.prefix = defaultPrefix.value
      codeRule.dateFormat = 'YYYYMMDD'
      codeRule.serialLength = 4
      codeRule.separator = ''
      codeRule.resetCycle = 'daily'
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Save code rule to backend
   */
  async function saveCodeRule() {
    loading.value = true
    try {
      await request.post(`/system/code-rules/by-code/${codeRuleType.value}/`, {
        company: appStore.currentCompany?.id,
        prefix: codeRule.prefix,
        date_format: codeRule.dateFormat,
        serial_length: codeRule.serialLength,
        separator: codeRule.separator,
        reset_cycle: codeRule.resetCycle
      })
      return true
    } catch (error) {
      console.error('Failed to save code rule:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Generate a new code
   * @returns {Promise<string>} Generated code
   */
  async function generateCode() {
    try {
      const res = await request.post('/system/code-rules/generate_code/', {
        company: appStore.currentCompany?.id,
        code_type: codeRuleType.value
      })
      
      if (res.code) {
        return res.code
      }
      
      throw new Error('No code returned')
    } catch (error) {
      console.error('Failed to generate code:', error)
      
      // Fallback to local generation
      const date = new Date()
      const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
      const random = String(Math.floor(Math.random() * 10000)).padStart(4, '0')
      
      return `${codeRule.prefix || defaultPrefix.value}${dateStr}${random}`
    }
  }
  
  /**
   * Update code rule values
   * @param {Object} values - New values to merge into codeRule
   */
  function updateCodeRule(values) {
    Object.assign(codeRule, values)
  }
  
  /**
   * Reset code rule to defaults
   */
  function resetCodeRule() {
    codeRule.prefix = defaultPrefix.value
    codeRule.dateFormat = 'YYYYMMDD'
    codeRule.serialLength = 4
    codeRule.separator = ''
    codeRule.resetCycle = 'daily'
  }
  
  return {
    // State
    loading,
    codeRule,
    codeExample,
    codeRuleType,
    defaultPrefix,
    
    // Methods
    loadCodeRule,
    saveCodeRule,
    generateCode,
    updateCodeRule,
    resetCodeRule,
  }
}

export default useCodeRule
