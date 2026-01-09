/**
 * Composables 导出
 * 
 * 遵循 .cursorrules 规约:
 * - 复杂交互逻辑必须提取到 @/composables
 */

// ==================== Universal Dynamic Form System ====================
// Dynamic module management - universal composable for any module
export { useDynamicModule } from './useDynamicModule'

// Code rule management - for modules with automatic code generation
export { useCodeRule } from './useCodeRule'

// Form configuration - loads and manages form configs
export { useFormConfig } from './useFormConfig'

// List management - search, filter, column settings, pagination
export {
  useListFilter,
  useColumnSettings,
  usePagination,
  useListManager
} from './useListToolbar'

// ==================== Asset Module Specific ====================
// 资产表单
export {
  useAssetFormData,
  useAssetFieldConfig,
  useAssetImage,
  useAssetSubmit,
  useAssetOptions
} from './useAssetForm'

// 资产选择
export {
  useAssetSearch,
  useUserDepartmentOptions
} from './useAssetSelect'

// ==================== Asset Operations ====================
// 借用相关
export {
  useBorrowForm,
  useReturnForm,
  useBorrowList,
  useBorrowStatus
} from './useBorrow'

// 领用相关
export {
  useReceiveForm,
  useReceiveReturnForm,
  useReceiveList,
  useReceiveStatus
} from './useReceive'
