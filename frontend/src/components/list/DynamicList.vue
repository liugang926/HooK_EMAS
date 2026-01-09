<template>
  <div class="dynamic-list-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>{{ moduleLabel }}</h2>
          <div class="header-actions">
            <slot name="header-actions">
              <el-button v-if="permissions.create" type="primary" @click="handleCreate">
                <el-icon><Plus /></el-icon>
                {{ createButtonText }}
              </el-button>
            </slot>
          </div>
        </div>
      </template>
      
      <!-- Search Toolbar -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            :placeholder="searchPlaceholder"
            clearable
            style="width: 280px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="toggleAdvanced">
            <el-icon><Filter /></el-icon>
            {{ showAdvanced ? '收起筛选' : '高级筛选' }}
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </div>

        <div class="toolbar-actions">
          <!-- Column Settings -->
          <el-popover placement="bottom-end" :width="280" trigger="click">
            <template #reference>
              <el-button>
                <el-icon><Setting /></el-icon>
                列设置
              </el-button>
            </template>
            <div class="column-settings">
              <div class="column-settings-header">
                <span>显示列配置</span>
                <el-button type="primary" link size="small" @click="resetColumns">恢复默认</el-button>
              </div>
              <el-checkbox-group v-model="visibleColumns" class="column-list">
                <div v-for="col in allColumns" :key="col.key" class="column-item">
                  <el-checkbox :value="col.key">{{ col.label }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </div>
          </el-popover>

          <el-button v-if="permissions.export" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
          
          <el-button v-if="permissions.import" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入
          </el-button>
        </div>
      </div>

      <!-- Advanced Filters -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <slot name="advanced-filters" :filter-form="filterForm">
            <el-form :model="filterForm" inline label-width="80px">
              <el-form-item 
                v-for="filter in advancedFilterFields" 
                :key="filter.key" 
                :label="filter.label"
              >
                <component
                  :is="getFilterComponent(filter.type)"
                  v-model="filterForm[filter.key]"
                  v-bind="getFilterProps(filter)"
                  style="width: 150px"
                  clearable
                />
              </el-form-item>
            </el-form>
          </slot>
        </div>
      </el-collapse-transition>
      
      <!-- Batch Operations Bar -->
      <div class="batch-bar" v-if="selectedRows.length > 0">
        <span class="selection-info">已选择 {{ selectedRows.length }} 项</span>
        <slot name="batch-actions" :selected="selectedRows">
          <el-button size="small" v-if="permissions.delete" type="danger" @click="handleBatchDelete">
            批量删除
          </el-button>
        </slot>
        <el-button size="small" link @click="clearSelection">清空选择</el-button>
      </div>
      
      <!-- Data Table -->
      <el-table 
        ref="tableRef"
        :data="tableData" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        @sort-change="handleSortChange"
        @row-click="handleRowClick"
      >
        <el-table-column v-if="selectable" type="selection" width="55" />
        
        <el-table-column
          v-for="col in displayColumns"
          :key="col.key"
          :prop="col.key"
          :label="col.label"
          :width="col.width"
          :min-width="col.minWidth"
          :sortable="col.sortable ? 'custom' : false"
          :show-overflow-tooltip="true"
        >
          <template #default="{ row }">
            <slot :name="`column-${col.key}`" :row="row" :value="row[col.key]">
              <span v-if="col.type === 'switch'">
                <el-tag :type="row[col.key] ? 'success' : 'info'" size="small">
                  {{ row[col.key] ? '是' : '否' }}
                </el-tag>
              </span>
              <span v-else-if="col.type === 'select'">
                {{ getOptionLabel(col, row[col.key]) }}
              </span>
              <span v-else-if="col.type === 'date'">
                {{ formatDate(row[col.key]) }}
              </span>
              <span v-else-if="col.type === 'datetime'">
                {{ formatDateTime(row[col.key]) }}
              </span>
              <span v-else-if="col.type === 'decimal' || col.type === 'number'">
                {{ formatNumber(row[col.key], col) }}
              </span>
              <span v-else>
                {{ row[col.key] ?? '-' }}
              </span>
            </slot>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" :width="actionColumnWidth" fixed="right">
          <template #default="{ row }">
            <slot name="row-actions" :row="row">
              <el-button type="primary" link @click.stop="handleView(row)">查看</el-button>
              <el-button v-if="permissions.edit" type="primary" link @click.stop="handleEdit(row)">编辑</el-button>
              <el-button v-if="permissions.delete" type="danger" link @click.stop="handleDelete(row)">删除</el-button>
            </slot>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- Dynamic Form Dialog -->
    <DynamicForm
      v-if="formDialogVisible"
      v-model="formDialogVisible"
      :module="module"
      :mode="formMode"
      :data="currentRecord"
      :record-id="currentRecordId"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />
    
    <!-- View Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="`查看${moduleLabel}`" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item
          v-for="col in allColumns"
          :key="col.key"
          :label="col.label"
          :span="col.type === 'textarea' ? 2 : 1"
        >
          <slot :name="`view-${col.key}`" :row="currentRecord" :value="currentRecord[col.key]">
            {{ formatFieldValue(col, currentRecord[col.key]) }}
          </slot>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button v-if="permissions.edit" type="primary" @click="handleEditFromView">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Search, Filter, Refresh, Setting, Download, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElInput, ElSelect, ElDatePicker, ElSwitch } from 'element-plus'
import DynamicForm from '@/components/form/DynamicForm.vue'
import { useDynamicModule } from '@/composables/useDynamicModule'

const props = defineProps({
  // Module identifier (e.g., 'asset', 'supply', 'user')
  module: {
    type: String,
    required: true
  },
  // Available actions
  actions: {
    type: Array,
    default: () => ['create', 'edit', 'delete', 'view']
  },
  // Enable row selection
  selectable: {
    type: Boolean,
    default: true
  },
  // Custom API endpoint (overrides module default)
  apiEndpoint: {
    type: String,
    default: null
  },
  // Enable tree mode for hierarchical data
  treeMode: {
    type: Boolean,
    default: false
  },
  // Custom search placeholder
  searchPlaceholder: {
    type: String,
    default: '搜索...'
  },
  // Create button text
  createButtonText: {
    type: String,
    default: '新增'
  },
  // Action column width
  actionColumnWidth: {
    type: [Number, String],
    default: 180
  }
})

const emit = defineEmits([
  'row-click',
  'create',
  'edit',
  'delete',
  'view',
  'selection-change',
  'data-loaded'
])

// Use dynamic module composable
const {
  moduleConfig,
  moduleLabel,
  fields,
  listFields,
  loading,
  loadModuleConfig,
  loadListFields,
  fetchData,
  deleteRecord,
  bulkDelete
} = useDynamicModule(props.module, props.apiEndpoint)

// Component state
const tableRef = ref(null)
const tableData = ref([])
const selectedRows = ref([])
const formDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const formMode = ref('create')
const currentRecord = ref(null)
const currentRecordId = ref(null)

// Search and filter state
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({})
const sortField = ref(null)
const sortOrder = ref(null)

// Pagination state
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

// Column visibility
const visibleColumns = ref([])
const defaultVisibleColumns = ref([])

// Computed properties
const permissions = computed(() => ({
  create: props.actions.includes('create'),
  edit: props.actions.includes('edit'),
  delete: props.actions.includes('delete'),
  view: props.actions.includes('view'),
  import: props.actions.includes('import'),
  export: props.actions.includes('export')
}))

const allColumns = computed(() => {
  return listFields.value.map(f => ({
    key: f.key,
    label: f.label,
    type: f.type,
    width: f.width,
    minWidth: f.minWidth || 100,
    sortable: f.sortable,
    searchable: f.searchable,
    options: f.options || []
  }))
})

const displayColumns = computed(() => {
  return allColumns.value.filter(col => visibleColumns.value.includes(col.key))
})

const advancedFilterFields = computed(() => {
  return listFields.value.filter(f => 
    f.searchable || ['select', 'date', 'switch'].includes(f.type)
  ).slice(0, 6) // Limit to 6 filter fields
})

// Methods
function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadData()
}

function handleReset() {
  searchKeyword.value = ''
  Object.keys(filterForm).forEach(key => {
    filterForm[key] = null
  })
  sortField.value = null
  sortOrder.value = null
  pagination.current = 1
  loadData()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  loadData()
}

function handleSortChange({ prop, order }) {
  sortField.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : null
  loadData()
}

function resetColumns() {
  visibleColumns.value = [...defaultVisibleColumns.value]
  saveColumnSettings()
}

function saveColumnSettings() {
  localStorage.setItem(`${props.module}_list_columns`, JSON.stringify(visibleColumns.value))
}

function loadColumnSettings() {
  const saved = localStorage.getItem(`${props.module}_list_columns`)
  if (saved) {
    try {
      visibleColumns.value = JSON.parse(saved)
    } catch (e) {
      visibleColumns.value = [...defaultVisibleColumns.value]
    }
  } else {
    visibleColumns.value = [...defaultVisibleColumns.value]
  }
}

async function loadData() {
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    // Add filter params
    Object.entries(filterForm).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params[key] = value
      }
    })
    
    // Add sort params
    if (sortField.value && sortOrder.value) {
      params.ordering = sortOrder.value === 'desc' ? `-${sortField.value}` : sortField.value
    }
    
    const result = await fetchData(params)
    tableData.value = result.results || result || []
    pagination.total = result.count || tableData.value.length
    
    emit('data-loaded', { data: tableData.value, total: pagination.total })
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  }
}

function handleSelectionChange(selection) {
  selectedRows.value = selection
  emit('selection-change', selection)
}

function clearSelection() {
  tableRef.value?.clearSelection()
  selectedRows.value = []
}

function handleRowClick(row) {
  emit('row-click', row)
}

function handleCreate() {
  formMode.value = 'create'
  currentRecord.value = null
  currentRecordId.value = null
  formDialogVisible.value = true
  emit('create')
}

function handleView(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
  emit('view', row)
}

function handleEdit(row) {
  formMode.value = 'edit'
  currentRecord.value = row
  currentRecordId.value = row.id
  formDialogVisible.value = true
  emit('edit', row)
}

function handleEditFromView() {
  viewDialogVisible.value = false
  handleEdit(currentRecord.value)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除该${moduleLabel.value}吗？`,
      '删除确认',
      { type: 'warning' }
    )
    
    await deleteRecord(row.id)
    ElMessage.success('删除成功')
    loadData()
    emit('delete', row)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 项吗？`,
      '批量删除确认',
      { type: 'warning' }
    )
    
    const ids = selectedRows.value.map(row => row.id)
    await bulkDelete(ids)
    
    ElMessage.success('批量删除成功')
    clearSelection()
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

function handleExport() {
  ElMessage.info('导出功能开发中...')
}

function handleImport() {
  ElMessage.info('导入功能开发中...')
}

function handleFormSuccess(data) {
  formDialogVisible.value = false
  loadData()
}

function handleFormCancel() {
  formDialogVisible.value = false
}

// Formatting helpers
function formatDate(value) {
  if (!value) return '-'
  return value.split('T')[0]
}

function formatDateTime(value) {
  if (!value) return '-'
  return value.replace('T', ' ').substring(0, 19)
}

function formatNumber(value, col) {
  if (value === null || value === undefined) return '-'
  const precision = col.numberConfig?.precision ?? 2
  return Number(value).toFixed(precision)
}

function getOptionLabel(col, value) {
  if (!value) return '-'
  const option = col.options?.find(opt => opt.value === value)
  return option?.label || value
}

function formatFieldValue(col, value) {
  if (value === null || value === undefined) return '-'
  
  switch (col.type) {
    case 'switch':
      return value ? '是' : '否'
    case 'select':
      return getOptionLabel(col, value)
    case 'date':
      return formatDate(value)
    case 'datetime':
      return formatDateTime(value)
    case 'decimal':
    case 'number':
      return formatNumber(value, col)
    default:
      return value
  }
}

function getFilterComponent(type) {
  switch (type) {
    case 'select':
      return ElSelect
    case 'date':
      return ElDatePicker
    case 'switch':
      return ElSwitch
    default:
      return ElInput
  }
}

function getFilterProps(filter) {
  const baseProps = {
    placeholder: `选择${filter.label}`
  }
  
  if (filter.type === 'select' && filter.options) {
    return {
      ...baseProps,
      filterable: true
    }
  }
  
  if (filter.type === 'date') {
    return {
      ...baseProps,
      type: 'date',
      valueFormat: 'YYYY-MM-DD'
    }
  }
  
  return baseProps
}

// Initialize
onMounted(async () => {
  await loadModuleConfig()
  await loadListFields()
  
  // Set default visible columns
  defaultVisibleColumns.value = listFields.value
    .filter(f => f.showInList !== false)
    .map(f => f.key)
  
  loadColumnSettings()
  loadData()
})

// Watch for column changes
watch(visibleColumns, () => {
  saveColumnSettings()
}, { deep: true })

// Expose methods for parent component
defineExpose({
  loadData,
  clearSelection,
  getSelectedRows: () => selectedRows.value
})
</script>

<style lang="scss" scoped>
.dynamic-list-container {
  .page-card {
    border-radius: 16px;
    
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      h2 {
        margin: 0;
        font-size: 18px;
        color: #1f2937;
      }
    }
  }
  
  .list-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    
    .toolbar-search {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    
    .toolbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .advanced-filters {
    padding: 16px;
    background: #fafafa;
    border-radius: 8px;
    margin-bottom: 16px;
    border: 1px dashed #e5e7eb;
    
    :deep(.el-form-item) {
      margin-bottom: 8px;
    }
  }
  
  .batch-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: #e6f7ff;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .selection-info {
      font-size: 14px;
      color: #1890ff;
      font-weight: 500;
    }
  }
  
  .column-settings {
    .column-settings-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #e5e7eb;
      font-weight: 500;
    }
    
    .column-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
      max-height: 300px;
      overflow-y: auto;
    }
    
    .column-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 8px;
      border-radius: 4px;
      
      &:hover {
        background: #f5f7fa;
      }
    }
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
