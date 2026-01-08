<template>
  <div class="list-toolbar">
    <!-- 搜索区域 -->
    <div class="toolbar-search">
      <el-input
        v-model="searchKeyword"
        :placeholder="searchPlaceholder"
        clearable
        style="width: 240px"
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

    <!-- 高级筛选区域 -->
    <el-collapse-transition>
      <div v-show="showAdvanced" class="toolbar-filters">
        <el-form :model="filterForm" inline label-width="80px">
          <!-- 状态筛选 -->
          <el-form-item v-if="statusOptions.length > 0" label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
              <el-option
                v-for="opt in statusOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </el-form-item>

          <!-- 部门筛选 -->
          <el-form-item v-if="showDepartment" label="部门">
            <el-tree-select
              v-model="filterForm.department"
              :data="departmentOptions"
              :props="{ value: 'id', label: 'name', children: 'children' }"
              placeholder="选择部门"
              check-strictly
              filterable
              clearable
              style="width: 180px"
            />
          </el-form-item>

          <!-- 人员筛选 -->
          <el-form-item v-if="showUser" label="人员">
            <el-select v-model="filterForm.user" filterable clearable placeholder="选择人员" style="width: 140px">
              <el-option
                v-for="user in userOptions"
                :key="user.id"
                :label="user.display_name || user.username"
                :value="user.id"
              />
            </el-select>
          </el-form-item>

          <!-- 日期范围 -->
          <el-form-item v-if="showDateRange" :label="dateLabel">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
          </el-form-item>

          <!-- 自定义筛选插槽 -->
          <slot name="filters" :filterForm="filterForm"></slot>
        </el-form>
      </div>
    </el-collapse-transition>

    <!-- 工具栏右侧 -->
    <div class="toolbar-actions">
      <slot name="actions"></slot>
      
      <!-- 列配置 -->
      <el-popover placement="bottom-end" :width="300" trigger="click">
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
            <div v-for="col in columnOrder" :key="col.prop" class="column-item">
              <el-checkbox :value="col.prop">{{ col.label }}</el-checkbox>
            </div>
          </el-checkbox-group>
        </div>
      </el-popover>

      <!-- 导出 -->
      <el-button v-if="showExport" @click="handleExport">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { Search, Filter, Refresh, Setting, Download } from '@element-plus/icons-vue'
import request from '@/utils/request'

const props = defineProps({
  // 搜索相关
  searchPlaceholder: {
    type: String,
    default: '搜索单号、资产名称...'
  },
  // 状态选项
  statusOptions: {
    type: Array,
    default: () => []
  },
  // 是否显示部门筛选
  showDepartment: {
    type: Boolean,
    default: true
  },
  // 是否显示人员筛选
  showUser: {
    type: Boolean,
    default: true
  },
  // 是否显示日期范围
  showDateRange: {
    type: Boolean,
    default: true
  },
  // 日期标签
  dateLabel: {
    type: String,
    default: '日期'
  },
  // 是否显示导出
  showExport: {
    type: Boolean,
    default: false
  },
  // 列配置
  columns: {
    type: Array,
    default: () => []
  },
  // 存储key（用于本地存储列配置）
  storageKey: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['search', 'filter', 'export', 'columns-change'])

const searchKeyword = ref('')
const showAdvanced = ref(false)
const departmentOptions = ref([])
const userOptions = ref([])

const filterForm = reactive({
  status: null,
  department: null,
  user: null,
  dateRange: null
})

// 列配置
const visibleColumns = ref([])
const columnOrder = ref([])

// 初始化列配置
onMounted(() => {
  loadDepartments()
  loadUsers()
  initColumnSettings()
})

// 从本地存储加载列配置
function initColumnSettings() {
  const storageKey = props.storageKey || 'default'
  const savedConfig = localStorage.getItem(`column_config_${storageKey}`)
  
  if (savedConfig) {
    try {
      const config = JSON.parse(savedConfig)
      visibleColumns.value = config.visible || props.columns.map(c => c.prop)
      columnOrder.value = config.order || [...props.columns]
    } catch (e) {
      resetColumns()
    }
  } else {
    resetColumns()
  }
}

// 重置列配置
function resetColumns() {
  visibleColumns.value = props.columns.map(c => c.prop)
  columnOrder.value = [...props.columns]
  saveColumnSettings()
}

// 保存列配置
function saveColumnSettings() {
  const storageKey = props.storageKey || 'default'
  localStorage.setItem(`column_config_${storageKey}`, JSON.stringify({
    visible: visibleColumns.value,
    order: columnOrder.value
  }))
}

// 监听列配置变化
watch([visibleColumns, columnOrder], () => {
  saveColumnSettings()
  emit('columns-change', {
    visible: visibleColumns.value,
    order: columnOrder.value
  })
}, { deep: true })

// 加载部门
async function loadDepartments() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    departmentOptions.value = res || []
  } catch (error) {
    console.error('加载部门失败:', error)
  }
}

// 加载用户
async function loadUsers() {
  try {
    const res = await request.get('/auth/users/', { params: { page_size: 1000 } })
    userOptions.value = res?.results || res || []
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

// 切换高级筛选
function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

// 搜索
function handleSearch() {
  emit('search', searchKeyword.value)
  emitFilter()
}

// 重置
function handleReset() {
  searchKeyword.value = ''
  filterForm.status = null
  filterForm.department = null
  filterForm.user = null
  filterForm.dateRange = null
  emit('search', '')
  emitFilter()
}

// 发送筛选事件
function emitFilter() {
  emit('filter', {
    search: searchKeyword.value,
    status: filterForm.status,
    department: filterForm.department,
    user: filterForm.user,
    date_after: filterForm.dateRange?.[0],
    date_before: filterForm.dateRange?.[1]
  })
}

// 监听筛选条件变化
watch(filterForm, () => {
  emitFilter()
}, { deep: true })

// 导出
function handleExport() {
  emit('export')
}

// 暴露方法给父组件
defineExpose({
  filterForm,
  searchKeyword,
  resetColumns
})
</script>

<style lang="scss" scoped>
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
  
  .toolbar-filters {
    width: 100%;
    padding-top: 16px;
    border-top: 1px dashed #e5e7eb;
    margin-top: 8px;
    
    :deep(.el-form-item) {
      margin-bottom: 8px;
    }
  }
  
  .toolbar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
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
    
    .drag-handle {
      cursor: move;
      color: #909399;
    }
  }
}
</style>
