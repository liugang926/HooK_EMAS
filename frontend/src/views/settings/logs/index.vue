<template>
  <div class="logs-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>系统日志</h2>
          <el-button type="primary" @click="handleExport" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="filter-form">
        <el-form-item label="操作类型">
          <el-select v-model="filterForm.action" placeholder="全部" clearable style="width: 150px" @change="handleSearch">
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="新增" value="create" />
            <el-option label="编辑" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="导出" value="export" />
            <el-option label="导入" value="import" />
            <el-option label="查看" value="view" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作模块">
          <el-select v-model="filterForm.module" placeholder="全部" clearable style="width: 150px" @change="handleSearch">
            <el-option label="系统" value="system" />
            <el-option label="资产管理" value="asset" />
            <el-option label="耗材管理" value="consumable" />
            <el-option label="采购管理" value="procurement" />
            <el-option label="盘点管理" value="inventory" />
            <el-option label="财务管理" value="finance" />
            <el-option label="组织管理" value="organization" />
            <el-option label="用户管理" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="filterForm.operator" placeholder="请输入" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="logList" v-loading="loading" style="width: 100%">
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" size="small">{{ getActionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作模块" width="120">
          <template #default="{ row }">
            {{ getModuleLabel(row.module) }}
          </template>
        </el-table-column>
        <el-table-column prop="content" label="操作内容" min-width="250" show-overflow-tooltip />
        <el-table-column label="操作人" width="100">
          <template #default="{ row }">
            {{ row.operator_name || row.operator?.display_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
    
    <!-- 详情弹窗 -->
    <el-dialog v-model="viewDialogVisible" title="日志详情" width="600px">
      <el-descriptions :column="2" border v-if="currentLog">
        <el-descriptions-item label="操作时间">{{ formatDateTime(currentLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentLog.operator_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionTagType(currentLog.action)" size="small">{{ getActionLabel(currentLog.action) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作模块">{{ getModuleLabel(currentLog.module) }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="User Agent" :span="2">
          <div style="word-break: break-all; font-size: 12px;">{{ currentLog.user_agent || '-' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="操作内容" :span="2">{{ currentLog.content }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const exporting = ref(false)

const filterForm = reactive({
  action: '',
  module: '',
  operator: '',
  dateRange: []
})

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0
})

const logList = ref([])

// 详情弹窗
const viewDialogVisible = ref(false)
const currentLog = ref(null)

// 操作类型映射
const actionMap = {
  login: '登录',
  logout: '登出',
  create: '新增',
  update: '编辑',
  delete: '删除',
  export: '导出',
  import: '导入',
  view: '查看'
}

// 模块映射
const moduleMap = {
  system: '系统',
  asset: '资产管理',
  consumable: '耗材管理',
  procurement: '采购管理',
  inventory: '盘点管理',
  finance: '财务管理',
  organization: '组织管理',
  user: '用户管理'
}

function getActionLabel(action) {
  return actionMap[action] || action
}

function getModuleLabel(module) {
  return moduleMap[module] || module
}

function getActionTagType(action) {
  const types = { 
    login: 'info', 
    logout: 'info',
    create: 'success', 
    update: 'warning', 
    delete: 'danger', 
    export: 'primary',
    import: 'primary',
    view: '' 
  }
  return types[action] || 'info'
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取日志列表
async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    if (filterForm.action) {
      params.action = filterForm.action
    }
    if (filterForm.module) {
      params.module = filterForm.module
    }
    if (filterForm.operator) {
      params.search = filterForm.operator
    }
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.created_at__gte = filterForm.dateRange[0] + 'T00:00:00'
      params.created_at__lte = filterForm.dateRange[1] + 'T23:59:59'
    }
    
    const res = await request.get('/system/logs/', { params })
    logList.value = res.results || []
    pagination.total = res.count || 0
  } catch (error) {
    console.error('获取日志列表失败:', error)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.current = 1
  fetchLogs()
}

function handleReset() {
  filterForm.action = ''
  filterForm.module = ''
  filterForm.operator = ''
  filterForm.dateRange = []
  handleSearch()
}

function handlePageChange(page) {
  pagination.current = page
  fetchLogs()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.current = 1
  fetchLogs()
}

function handleView(row) {
  currentLog.value = row
  viewDialogVisible.value = true
}

async function handleExport() {
  exporting.value = true
  try {
    const params = {}
    if (filterForm.action) params.action = filterForm.action
    if (filterForm.module) params.module = filterForm.module
    if (filterForm.operator) params.search = filterForm.operator
    if (filterForm.dateRange && filterForm.dateRange.length === 2) {
      params.created_at__gte = filterForm.dateRange[0] + 'T00:00:00'
      params.created_at__lte = filterForm.dateRange[1] + 'T23:59:59'
    }
    
    // 获取所有符合条件的日志
    params.page_size = 10000
    const res = await request.get('/system/logs/', { params })
    const logs = res.results || []
    
    // 生成 CSV 内容
    const headers = ['操作时间', '操作类型', '操作模块', '操作内容', '操作人', 'IP地址']
    const rows = logs.map(log => [
      formatDateTime(log.created_at),
      getActionLabel(log.action),
      getModuleLabel(log.module),
      log.content,
      log.operator_name || '-',
      log.ip_address || '-'
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n')
    
    // 下载文件
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `系统日志_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style lang="scss" scoped>
.logs-container {
  .page-card { border-radius: 16px; }
  .page-header { display: flex; justify-content: space-between; align-items: center; h2 { margin: 0; font-size: 18px; color: #1f2937; } }
  .filter-form { margin-bottom: 20px; }
  .pagination-container { display: flex; justify-content: flex-end; margin-top: 20px; }
}
</style>
