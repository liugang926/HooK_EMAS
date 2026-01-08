<template>
  <div class="asset-receive-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产领用 & 退还</h2>
          <div class="header-actions">
            <el-button type="primary" @click="handleNewReceive">
              <el-icon><Plus /></el-icon>
              新建领用
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索筛选工具栏 -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索单号、资产名称、领用人..."
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
          <!-- 列配置 -->
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
                <div v-for="col in allColumns" :key="col.prop" class="column-item">
                  <el-checkbox :value="col.prop">{{ col.label }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </div>
          </el-popover>

          <el-button @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>

      <!-- 高级筛选 -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <el-form :model="filterForm" inline label-width="80px">
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
                <el-option label="草稿" value="draft" />
                <el-option label="待审批" value="pending" />
                <el-option label="已通过" value="approved" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="领用部门">
              <el-tree-select
                v-model="filterForm.department"
                :data="departmentOptions"
                :props="{ value: 'id', label: 'displayName', children: 'children' }"
                placeholder="选择部门"
                check-strictly
                filterable
                clearable
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="领用人">
              <el-select v-model="filterForm.user" filterable clearable placeholder="选择领用人" style="width: 140px">
                <el-option
                  v-for="user in userOptions"
                  :key="user.id"
                  :label="user.display_name || user.username"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="领用日期">
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
          </el-form>
        </div>
      </el-collapse-transition>
      
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="领用记录" name="receive">
          <el-table :data="receiveList" style="width: 100%" v-loading="loading">
            <el-table-column v-if="isColumnVisible('receive_no')" prop="receive_no" label="领用单号" width="160" sortable />
            <el-table-column v-if="isColumnVisible('asset_info')" label="资产信息" min-width="220">
              <template #default="{ row }">
                <div v-for="item in row.items" :key="item.id" class="asset-info">
                  {{ item.asset_name || item.asset?.name }} ({{ item.asset_code || item.asset?.asset_code }})
                </div>
              </template>
            </el-table-column>
            <el-table-column v-if="isColumnVisible('receive_user_name')" prop="receive_user_name" label="领用人" width="100" />
            <el-table-column v-if="isColumnVisible('receive_department_name')" prop="receive_department_name" label="领用部门" width="140" />
            <el-table-column v-if="isColumnVisible('receive_date')" prop="receive_date" label="领用日期" width="120" sortable />
            <el-table-column v-if="isColumnVisible('status')" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column v-if="isColumnVisible('created_at')" prop="created_at" label="创建时间" width="170" sortable>
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleView(row)">查看</el-button>
                <el-button
                  v-if="row.status === 'completed'"
                  type="warning"
                  link
                  @click="handleReturn(row)"
                >
                  退还
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="退还记录" name="return">
          <el-table :data="returnList" style="width: 100%" v-loading="loading">
            <el-table-column prop="return_no" label="退还单号" width="160" />
            <el-table-column label="资产信息" min-width="220">
              <template #default="{ row }">
                <div>{{ row.asset_name }} ({{ row.asset_code }})</div>
              </template>
            </el-table-column>
            <el-table-column prop="return_user_name" label="退还人" width="100" />
            <el-table-column prop="return_date" label="退还日期" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getReturnStatusType(row.status)">{{ getReturnStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleViewReturn(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      
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
    
    <!-- 新建领用对话框 -->
    <el-dialog v-model="receiveDialogVisible" title="新建领用" width="700px">
      <el-form ref="receiveFormRef" :model="receiveForm" :rules="receiveRules" label-width="100px">
        <el-form-item label="选择资产" prop="assets">
          <el-select
            v-model="receiveForm.assets"
            multiple
            filterable
            remote
            :remote-method="searchAssets"
            :loading="searchingAssets"
            placeholder="请选择要领用的资产"
            style="width: 100%"
          >
            <el-option
              v-for="asset in availableAssets"
              :key="asset.id"
              :label="`${asset.name} (${asset.asset_code})`"
              :value="asset.id"
            />
          </el-select>
          <div class="tip">仅显示状态为"闲置"的资产</div>
        </el-form-item>
        <el-form-item label="领用人" prop="receive_user">
          <el-select v-model="receiveForm.receive_user" filterable placeholder="请选择领用人" style="width: 100%">
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="领用部门" prop="receive_department">
          <el-tree-select
            v-model="receiveForm.receive_department"
            :data="departmentOptions"
            :props="{ value: 'id', label: 'displayName', children: 'children' }"
            placeholder="请选择领用部门"
            check-strictly
            filterable
            :filter-node-method="filterDepartment"
            style="width: 100%"
            clearable
          />
        </el-form-item>
        <el-form-item label="领用日期" prop="receive_date">
          <el-date-picker
            v-model="receiveForm.receive_date"
            type="date"
            placeholder="请选择领用日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="receiveForm.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReceive">确认领用</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="领用详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="领用单号">{{ currentRecord.receive_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">{{ getStatusLabel(currentRecord.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="领用人">{{ currentRecord.receive_user_name }}</el-descriptions-item>
        <el-descriptions-item label="领用部门">{{ currentRecord.receive_department_name }}</el-descriptions-item>
        <el-descriptions-item label="领用日期">{{ currentRecord.receive_date }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ currentRecord.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin: 16px 0 8px;">领用资产</h4>
      <el-table :data="currentRecord?.items || []" border size="small">
        <el-table-column prop="asset_name" label="资产名称" />
        <el-table-column prop="asset_code" label="资产编号" width="150" />
        <el-table-column prop="status_display" label="状态" width="100" />
      </el-table>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="currentRecord && currentRecord.status === 'completed'" 
          type="warning" 
          @click="handleReturnFromDetail"
        >
          退还
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 退还对话框 -->
    <el-dialog v-model="returnDialogVisible" title="资产退还" width="600px">
      <el-form ref="returnFormRef" :model="returnForm" :rules="returnRules" label-width="100px">
        <el-form-item label="退还资产">
          <el-select
            v-model="returnForm.asset_ids"
            multiple
            placeholder="请选择要退还的资产"
            style="width: 100%"
          >
            <el-option
              v-for="item in currentRecord?.items || []"
              :key="item.asset"
              :label="`${item.asset_name} (${item.asset_code})`"
              :value="item.asset"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="退还日期" prop="return_date">
          <el-date-picker
            v-model="returnForm.return_date"
            type="date"
            placeholder="请选择退还日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="退还原因">
          <el-input v-model="returnForm.reason" type="textarea" :rows="3" placeholder="请输入退还原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReturn">确认退还</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, Search, Filter, Refresh, Setting, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

// ===== 状态定义 =====
const activeTab = ref('receive')
const loading = ref(false)
const submitting = ref(false)
const receiveDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const returnDialogVisible = ref(false)
const currentRecord = ref(null)
const searchingAssets = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({
  status: null,
  department: null,
  user: null,
  dateRange: null
})

// 列配置
const allColumns = [
  { prop: 'receive_no', label: '领用单号' },
  { prop: 'asset_info', label: '资产信息' },
  { prop: 'receive_user_name', label: '领用人' },
  { prop: 'receive_department_name', label: '领用部门' },
  { prop: 'receive_date', label: '领用日期' },
  { prop: 'status', label: '状态' },
  { prop: 'created_at', label: '创建时间' }
]
const visibleColumns = ref(['receive_no', 'asset_info', 'receive_user_name', 'receive_department_name', 'receive_date', 'status'])

const receiveFormRef = ref()
const returnFormRef = ref()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const receiveList = ref([])
const returnList = ref([])
const availableAssets = ref([])
const userOptions = ref([])
const departmentOptions = ref([])

const receiveForm = reactive({
  assets: [],
  receive_user: null,
  receive_department: null,
  receive_date: new Date().toISOString().split('T')[0],
  remark: ''
})

const returnForm = reactive({
  receive_id: null,
  asset_ids: [],
  return_date: new Date().toISOString().split('T')[0],
  reason: ''
})

const receiveRules = {
  assets: [{ required: true, message: '请选择要领用的资产', trigger: 'change' }],
  receive_user: [{ required: true, message: '请选择领用人', trigger: 'change' }],
  receive_date: [{ required: true, message: '请选择领用日期', trigger: 'change' }]
}

const returnRules = {
  return_date: [{ required: true, message: '请选择退还日期', trigger: 'change' }]
}

// ===== 状态映射 =====
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  pending: { label: '待审批', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  completed: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'info' }
}

const returnStatusMap = {
  pending: { label: '待处理', type: 'warning' },
  completed: { label: '已完成', type: 'success' }
}

// ===== 辅助方法 =====
function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

function getReturnStatusType(status) {
  return returnStatusMap[status]?.type || 'info'
}

function getReturnStatusLabel(status) {
  return returnStatusMap[status]?.label || status
}

function formatDateTime(dt) {
  if (!dt) return '-'
  return dt.replace('T', ' ').substring(0, 19)
}

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

// ===== 搜索筛选方法 =====
function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadData()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.status = null
  filterForm.department = null
  filterForm.user = null
  filterForm.dateRange = null
  pagination.current = 1
  loadData()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  loadData()
}

function resetColumns() {
  visibleColumns.value = ['receive_no', 'asset_info', 'receive_user_name', 'receive_department_name', 'receive_date', 'status']
}

function handleExport() {
  ElMessage.info('导出功能开发中...')
}

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.current = 1
  loadData()
}, { deep: true })

// ===== 数据加载方法 =====
async function loadData() {
  if (activeTab.value === 'receive') {
    await loadReceiveList()
  } else {
    await loadReturnList()
  }
}

async function loadReceiveList() {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    // 添加搜索条件
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.department) {
      params.receive_department = filterForm.department
    }
    if (filterForm.user) {
      params.receive_user = filterForm.user
    }
    if (filterForm.dateRange?.[0]) {
      params.receive_date_after = filterForm.dateRange[0]
    }
    if (filterForm.dateRange?.[1]) {
      params.receive_date_before = filterForm.dateRange[1]
    }
    
    const res = await request.get('/assets/receives/', { params })
    receiveList.value = res?.results || res || []
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载领用记录失败:', error)
    ElMessage.error('加载领用记录失败')
  } finally {
    loading.value = false
  }
}

async function loadReturnList() {
  loading.value = true
  try {
    const params = {
      operation_type: 'return',
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    
    const res = await request.get('/assets/operations/', { params })
    returnList.value = (res?.results || res || []).map(op => ({
      id: op.id,
      return_no: op.operation_no || `TH-${op.id}`,
      asset_name: op.asset_name,
      asset_code: op.asset_code,
      return_user_name: op.operator_name,
      return_date: op.created_at?.split('T')[0],
      status: 'completed',
      reason: op.description
    }))
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载退还记录失败:', error)
  } finally {
    loading.value = false
  }
}

async function searchAssets(query) {
  searchingAssets.value = true
  try {
    const res = await request.get('/assets/list/', {
      params: {
        status: 'idle',
        search: query,
        page_size: 50
      }
    })
    availableAssets.value = res?.results || res || []
  } catch (error) {
    console.error('搜索资产失败:', error)
  } finally {
    searchingAssets.value = false
  }
}

function filterDepartment(value, data) {
  if (!value) return true
  const searchValue = value.toLowerCase()
  return data.name.toLowerCase().includes(searchValue) || 
         (data.fullPath && data.fullPath.toLowerCase().includes(searchValue))
}

async function loadUsers() {
  try {
    const res = await request.get('/auth/users/', { params: { page_size: 1000 } })
    userOptions.value = res?.results || res || []
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

async function loadDepartments() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    const data = res || []
    departmentOptions.value = addPathToTree(data, '')
  } catch (error) {
    console.error('加载部门失败:', error)
  }
}

function addPathToTree(nodes, parentPath) {
  return nodes.map(node => {
    const currentPath = parentPath ? `${parentPath} > ${node.name}` : node.name
    const result = {
      ...node,
      displayName: parentPath ? `${node.name} (${parentPath})` : node.name,
      fullPath: currentPath
    }
    if (node.children && node.children.length > 0) {
      result.children = addPathToTree(node.children, currentPath)
    }
    return result
  })
}

// ===== 事件处理方法 =====
function handleTabChange() {
  pagination.current = 1
  loadData()
}

function handleNewReceive() {
  receiveForm.assets = []
  receiveForm.receive_user = null
  receiveForm.receive_department = null
  receiveForm.receive_date = new Date().toISOString().split('T')[0]
  receiveForm.remark = ''
  searchAssets('')
  receiveDialogVisible.value = true
}

function handleView(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
}

function handleViewReturn(row) {
  ElMessage.info(`退还单号：${row.return_no}`)
}

function handleReturn(row) {
  currentRecord.value = row
  returnForm.receive_id = row.id
  returnForm.asset_ids = row.items?.map(item => item.asset) || []
  returnForm.return_date = new Date().toISOString().split('T')[0]
  returnForm.reason = ''
  returnDialogVisible.value = true
}

function handleReturnFromDetail() {
  viewDialogVisible.value = false
  handleReturn(currentRecord.value)
}

async function submitReceive() {
  try {
    await receiveFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      receive_user: receiveForm.receive_user,
      receive_department: receiveForm.receive_department,
      receive_date: receiveForm.receive_date,
      remark: receiveForm.remark,
      items_data: receiveForm.assets.map(assetId => ({ 
        asset: assetId,
        remark: receiveForm.remark || ''
      }))
    }
    
    await request.post('/assets/receives/', data)
    ElMessage.success('领用成功')
    receiveDialogVisible.value = false
    loadReceiveList()
  } catch (error) {
    console.error('领用失败:', error)
    ElMessage.error('领用失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

async function submitReturn() {
  try {
    await returnFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  if (returnForm.asset_ids.length === 0) {
    ElMessage.warning('请选择要退还的资产')
    return
  }
  
  submitting.value = true
  try {
    await request.post(`/assets/receives/${returnForm.receive_id}/return_assets/`, {
      asset_ids: returnForm.asset_ids,
      return_date: returnForm.return_date,
      reason: returnForm.reason
    })
    
    ElMessage.success('退还成功')
    returnDialogVisible.value = false
    loadReceiveList()
    if (activeTab.value === 'return') {
      loadReturnList()
    }
  } catch (error) {
    console.error('退还失败:', error)
    ElMessage.error('退还失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

// ===== 初始化 =====
onMounted(() => {
  loadReceiveList()
  loadUsers()
  loadDepartments()
  
  // 从本地存储恢复列配置
  const savedColumns = localStorage.getItem('receive_columns')
  if (savedColumns) {
    try {
      visibleColumns.value = JSON.parse(savedColumns)
    } catch (e) {
      // ignore
    }
  }
})

// 监听列配置变化，保存到本地存储
watch(visibleColumns, (val) => {
  localStorage.setItem('receive_columns', JSON.stringify(val))
}, { deep: true })
</script>

<style lang="scss" scoped>
.asset-receive-container {
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
  
  .asset-info {
    line-height: 1.8;
  }
  
  .tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
