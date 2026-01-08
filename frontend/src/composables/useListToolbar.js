/**
 * 列表工具栏 Composable
 * 
 * 遵循 .cursorrules 规约:
 * - 复杂交互逻辑必须提取到 @/composables
 * 
 * 提供通用的列表搜索、筛选、列配置功能
 */
import { ref, reactive, watch } from 'vue'

/**
 * 搜索筛选逻辑
 */
export function useListFilter(defaultFilters = {}) {
  const searchKeyword = ref('')
  const showAdvanced = ref(false)
  const filterForm = reactive({ ...defaultFilters })
  
  function toggleAdvanced() {
    showAdvanced.value = !showAdvanced.value
  }
  
  function resetFilters() {
    searchKeyword.value = ''
    Object.keys(defaultFilters).forEach(key => {
      filterForm[key] = defaultFilters[key]
    })
  }
  
  function getFilterParams() {
    const params = {}
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    Object.entries(filterForm).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        // 处理日期范围
        if (key === 'dateRange' && Array.isArray(value) && value.length === 2) {
          params.start_date = value[0]
          params.end_date = value[1]
        } else {
          params[key] = value
        }
      }
    })
    
    return params
  }
  
  return {
    searchKeyword,
    showAdvanced,
    filterForm,
    toggleAdvanced,
    resetFilters,
    getFilterParams
  }
}

/**
 * 列配置逻辑
 */
export function useColumnSettings(storageKey, defaultColumns) {
  // 从 localStorage 获取保存的配置
  const savedColumns = localStorage.getItem(storageKey)
  const initialColumns = savedColumns 
    ? JSON.parse(savedColumns) 
    : defaultColumns.map(col => col.prop)
  
  const allColumns = ref(defaultColumns)
  const visibleColumns = ref(initialColumns)
  
  // 监听变化并保存到 localStorage
  watch(visibleColumns, (newVal) => {
    localStorage.setItem(storageKey, JSON.stringify(newVal))
  }, { deep: true })
  
  function resetColumns() {
    visibleColumns.value = defaultColumns.map(col => col.prop)
    localStorage.removeItem(storageKey)
  }
  
  function isColumnVisible(prop) {
    return visibleColumns.value.includes(prop)
  }
  
  return {
    allColumns,
    visibleColumns,
    resetColumns,
    isColumnVisible
  }
}

/**
 * 分页逻辑
 */
export function usePagination(defaultPageSize = 10) {
  const pagination = reactive({
    current: 1,
    pageSize: defaultPageSize,
    total: 0
  })
  
  function handleCurrentChange(page) {
    pagination.current = page
  }
  
  function handleSizeChange(size) {
    pagination.pageSize = size
    pagination.current = 1
  }
  
  function resetPagination() {
    pagination.current = 1
    pagination.total = 0
  }
  
  return {
    pagination,
    handleCurrentChange,
    handleSizeChange,
    resetPagination
  }
}

/**
 * 组合使用的列表管理
 */
export function useListManager(options = {}) {
  const {
    storageKey = 'list_columns',
    defaultColumns = [],
    defaultFilters = {},
    defaultPageSize = 10
  } = options
  
  const filter = useListFilter(defaultFilters)
  const columns = useColumnSettings(storageKey, defaultColumns)
  const page = usePagination(defaultPageSize)
  
  return {
    ...filter,
    ...columns,
    ...page
  }
}
