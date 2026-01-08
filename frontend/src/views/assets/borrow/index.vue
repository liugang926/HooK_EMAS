<template>
  <div class="asset-borrow-container">
    <!-- 借用统计卡片 -->
    <el-row :gutter="16" class="stats-row" v-if="statistics">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.borrowing_count }}</div>
            <div class="stat-label">借用中</div>
          </div>
          <el-icon class="stat-icon" :style="{ color: '#409EFF' }"><Document /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning" @click="showOverdue">
          <div class="stat-content">
            <div class="stat-number" :class="{ 'text-danger': statistics.overdue_count > 0 }">
              {{ statistics.overdue_count }}
            </div>
            <div class="stat-label">已超期</div>
          </div>
          <el-icon class="stat-icon" :style="{ color: '#E6A23C' }"><Warning /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" @click="showUpcoming">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.upcoming_count }}</div>
            <div class="stat-label">即将到期(7天内)</div>
          </div>
          <el-icon class="stat-icon" :style="{ color: '#67C23A' }"><Clock /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ statistics.this_month_count }}</div>
            <div class="stat-label">本月借用</div>
          </div>
          <el-icon class="stat-icon" :style="{ color: '#909399' }"><Calendar /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产借用 & 归还</h2>
          <el-button type="primary" @click="handleNewBorrow">
            <el-icon><Plus /></el-icon>
            新建借用
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选工具栏 -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索单号、资产名称、借用人..."
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
        </div>
      </div>

      <!-- 高级筛选 -->
      <el-collapse-transition>
        <div v-show="showAdvanced" class="advanced-filters">
          <el-form :model="filterForm" inline label-width="80px">
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部状态" clearable style="width: 140px">
                <el-option label="草稿" value="draft" />
                <el-option label="借用中" value="borrowed" />
                <el-option label="已归还" value="returned" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="借用部门">
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
            <el-form-item label="借用人">
              <el-select v-model="filterForm.user" filterable clearable placeholder="选择借用人" style="width: 140px">
                <el-option
                  v-for="user in userOptions"
                  :key="user.id"
                  :label="user.display_name || user.username"
                  :value="user.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="借用日期">
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
        <el-tab-pane label="借用记录" name="borrow">
          <el-table :data="borrowList" style="width: 100%" v-loading="loading">
            <el-table-column prop="borrow_no" label="借用单号" width="150" />
            <el-table-column label="资产信息" min-width="200">
              <template #default="{ row }">
                <div v-for="item in row.items" :key="item.id" class="asset-info">
                  <span :class="{ 'returned-item': item.is_returned }">
                    {{ item.asset_name || item.asset?.name }} ({{ item.asset_code || item.asset?.asset_code }})
                    <el-tag v-if="item.is_returned" size="small" type="success">已归还</el-tag>
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="borrow_user_name" label="借用人" width="100" />
            <el-table-column prop="borrow_department_name" label="借用部门" width="120" />
            <el-table-column prop="borrow_date" label="借用日期" width="120" />
            <el-table-column label="预计归还" width="120">
              <template #default="{ row }">
                <span :class="getExpiredClass(row)">
                  {{ row.expected_return_date || '-' }}
                  <el-icon v-if="isOverdue(row)" class="overdue-icon"><Warning /></el-icon>
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleView(row)">查看</el-button>
                <el-button 
                  v-if="hasUnreturnedItems(row)" 
                  type="success" 
                  link 
                  @click="handleReturnAsset(row)"
                >
                  归还
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane name="pending">
          <template #label>
            <span>
              待归还
              <el-badge v-if="pendingReturnCount > 0" :value="pendingReturnCount" class="tab-badge" />
            </span>
          </template>
          <div class="filter-bar">
            <el-radio-group v-model="pendingFilter" @change="loadPendingReturns">
              <el-radio-button value="all">全部</el-radio-button>
              <el-radio-button value="overdue">已超期</el-radio-button>
              <el-radio-button value="upcoming">即将到期</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="pendingReturnList" style="width: 100%" v-loading="loading">
            <el-table-column prop="borrow_no" label="借用单号" width="150" />
            <el-table-column label="未归还资产" min-width="200">
              <template #default="{ row }">
                <div v-for="item in row.unreturned_items" :key="item.id" class="asset-info">
                  {{ item.asset_name }} ({{ item.asset_code }})
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="borrower" label="借用人" width="100" />
            <el-table-column prop="borrow_department" label="借用部门" width="120" />
            <el-table-column prop="borrow_date" label="借用日期" width="120" />
            <el-table-column label="预计归还" width="120">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.is_overdue, 'text-warning': !row.is_overdue && row.days_remaining <= 7 }">
                  {{ row.expected_return_date || '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.is_overdue" type="danger">
                  超期 {{ Math.abs(row.days_remaining) }} 天
                </el-tag>
                <el-tag v-else-if="row.days_remaining !== null && row.days_remaining <= 7" type="warning">
                  {{ row.days_remaining }} 天后到期
                </el-tag>
                <el-tag v-else type="info">
                  {{ row.days_remaining !== null ? row.days_remaining + ' 天后到期' : '未设置' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleViewPending(row)">查看</el-button>
                <el-button type="success" link @click="handleReturnPending(row)">归还</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="归还记录" name="return">
          <el-table :data="returnList" style="width: 100%" v-loading="loading">
            <el-table-column prop="return_no" label="归还单号" width="150" />
            <el-table-column label="资产信息" min-width="200">
              <template #default="{ row }">
                <div>{{ row.asset_name }} ({{ row.asset_code }})</div>
              </template>
            </el-table-column>
            <el-table-column prop="return_user_name" label="归还人" width="100" />
            <el-table-column prop="return_date" label="归还日期" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag type="success">已完成</el-tag>
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
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- 新建借用对话框 -->
    <el-dialog v-model="borrowDialogVisible" title="新建借用" width="700px">
      <el-form ref="borrowFormRef" :model="borrowForm" :rules="borrowRules" label-width="100px">
        <el-form-item label="选择资产" prop="assets">
          <el-select
            v-model="borrowForm.assets"
            multiple
            filterable
            remote
            :remote-method="searchAssets"
            :loading="searchingAssets"
            placeholder="请选择要借用的资产"
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
        <el-form-item label="借用人" prop="borrow_user">
          <el-select v-model="borrowForm.borrow_user" filterable placeholder="请选择借用人" style="width: 100%">
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借用部门">
          <el-tree-select
            v-model="borrowForm.borrow_department"
            :data="departmentOptions"
            :props="{ value: 'id', label: 'displayName', children: 'children' }"
            placeholder="请选择借用部门"
            check-strictly
            filterable
            :filter-node-method="filterDepartment"
            style="width: 100%"
            clearable
          />
        </el-form-item>
        <el-form-item label="借用日期" prop="borrow_date">
          <el-date-picker
            v-model="borrowForm.borrow_date"
            type="date"
            placeholder="请选择借用日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预计归还" prop="expected_return_date">
          <el-date-picker
            v-model="borrowForm.expected_return_date"
            type="date"
            placeholder="请选择预计归还日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="借用原因">
          <el-input v-model="borrowForm.reason" type="textarea" :rows="3" placeholder="请输入借用原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitBorrow">确认借用</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="借用详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="借用单号">{{ currentRecord.borrow_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">{{ getStatusLabel(currentRecord.status) }}</el-tag>
          <el-tag v-if="isOverdue(currentRecord)" type="danger" style="margin-left: 8px;">已超期</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="借用人">{{ currentRecord.borrow_user_name || currentRecord.borrower }}</el-descriptions-item>
        <el-descriptions-item label="借用部门">{{ currentRecord.borrow_department_name || currentRecord.borrow_department }}</el-descriptions-item>
        <el-descriptions-item label="借用日期">{{ currentRecord.borrow_date }}</el-descriptions-item>
        <el-descriptions-item label="预计归还">
          <span :class="{ 'text-danger': isOverdue(currentRecord) }">
            {{ currentRecord.expected_return_date || '-' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="实际归还">{{ currentRecord.actual_return_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="借用原因">{{ currentRecord.reason || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin: 16px 0 8px;">借用资产</h4>
      <el-table :data="currentRecord?.items || currentRecord?.unreturned_items || []" border size="small">
        <el-table-column prop="asset_name" label="资产名称" />
        <el-table-column prop="asset_code" label="资产编号" width="150" />
        <el-table-column label="归还状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_returned" type="success">已归还</el-tag>
            <el-tag v-else type="warning">未归还</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="return_date" label="归还日期" width="120">
          <template #default="{ row }">
            {{ row.return_date || '-' }}
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="currentRecord && hasUnreturnedItems(currentRecord)" 
          type="success" 
          @click="handleReturnFromDetail"
        >
          归还
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 归还确认对话框 -->
    <el-dialog v-model="returnDialogVisible" title="资产归还" width="600px">
      <el-form ref="returnFormRef" :model="returnForm" :rules="returnRules" label-width="100px">
        <el-form-item label="归还资产">
          <el-select
            v-model="returnForm.asset_ids"
            multiple
            placeholder="请选择要归还的资产"
            style="width: 100%"
          >
            <el-option
              v-for="item in getUnreturnedItems(currentRecord)"
              :key="item.asset || item.asset_id"
              :label="`${item.asset_name} (${item.asset_code})`"
              :value="item.asset || item.asset_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="归还日期" prop="return_date">
          <el-date-picker
            v-model="returnForm.return_date"
            type="date"
            placeholder="请选择归还日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="资产状况">
          <el-select v-model="returnForm.condition" placeholder="请选择资产状况" style="width: 100%">
            <el-option label="完好" value="good" />
            <el-option label="轻微损坏" value="minor_damage" />
            <el-option label="严重损坏" value="major_damage" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="returnForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReturn">确认归还</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Plus, Warning, Clock, Calendar, Document, Search, Filter, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const activeTab = ref('borrow')
const loading = ref(false)
const submitting = ref(false)
const borrowDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const returnDialogVisible = ref(false)

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
  { prop: 'borrow_no', label: '借用单号' },
  { prop: 'asset_info', label: '资产信息' },
  { prop: 'borrow_user_name', label: '借用人' },
  { prop: 'borrow_department_name', label: '借用部门' },
  { prop: 'borrow_date', label: '借用日期' },
  { prop: 'expected_return_date', label: '预计归还' },
  { prop: 'status', label: '状态' }
]
const visibleColumns = ref(['borrow_no', 'asset_info', 'borrow_user_name', 'borrow_department_name', 'borrow_date', 'expected_return_date', 'status'])

function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadBorrowList()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.status = null
  filterForm.department = null
  filterForm.user = null
  filterForm.dateRange = null
  pagination.current = 1
  loadBorrowList()
}

function resetColumns() {
  visibleColumns.value = ['borrow_no', 'asset_info', 'borrow_user_name', 'borrow_department_name', 'borrow_date', 'expected_return_date', 'status']
}

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.current = 1
  loadBorrowList()
}, { deep: true })
const currentRecord = ref(null)
const searchingAssets = ref(false)
const pendingFilter = ref('all')

const borrowFormRef = ref()
const returnFormRef = ref()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const borrowList = ref([])
const returnList = ref([])
const pendingReturnList = ref([])
const availableAssets = ref([])
const userOptions = ref([])
const departmentOptions = ref([])
const statistics = ref(null)

const pendingReturnCount = computed(() => {
  return statistics.value?.overdue_count + statistics.value?.upcoming_count || 0
})

const borrowForm = reactive({
  assets: [],
  borrow_user: null,
  borrow_department: null,
  borrow_date: new Date().toISOString().split('T')[0],
  expected_return_date: '',
  reason: ''
})

const returnForm = reactive({
  borrow_id: null,
  asset_ids: [],
  return_date: new Date().toISOString().split('T')[0],
  condition: 'good',
  remark: ''
})

const borrowRules = {
  assets: [{ required: true, message: '请选择要借用的资产', trigger: 'change' }],
  borrow_user: [{ required: true, message: '请选择借用人', trigger: 'change' }],
  borrow_date: [{ required: true, message: '请选择借用日期', trigger: 'change' }],
  expected_return_date: [{ required: true, message: '请选择预计归还日期', trigger: 'change' }]
}

const returnRules = {
  return_date: [{ required: true, message: '请选择归还日期', trigger: 'change' }]
}

// 状态映射
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  pending: { label: '待审批', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  borrowed: { label: '借用中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  returned: { label: '已归还', type: 'success' },
  cancelled: { label: '已取消', type: 'info' }
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

// 判断是否超期
function isOverdue(row) {
  if (!row || !row.expected_return_date) return false
  if (row.status === 'returned') return false
  const today = new Date().toISOString().split('T')[0]
  return row.expected_return_date < today && hasUnreturnedItems(row)
}

// 获取超期样式类
function getExpiredClass(row) {
  if (isOverdue(row)) return 'text-danger'
  if (!row.expected_return_date) return ''
  
  const today = new Date()
  const expDate = new Date(row.expected_return_date)
  const diffDays = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24))
  
  if (diffDays <= 7 && diffDays >= 0 && hasUnreturnedItems(row)) return 'text-warning'
  return ''
}

// 判断是否有未归还资产
function hasUnreturnedItems(row) {
  if (!row) return false
  // 如果是待归还列表的数据
  if (row.unreturned_items) return row.unreturned_items.length > 0
  // 如果是借用记录的数据
  if (row.items) return row.items.some(item => !item.is_returned)
  return false
}

// 获取未归还的资产
function getUnreturnedItems(row) {
  if (!row) return []
  if (row.unreturned_items) return row.unreturned_items
  if (row.items) return row.items.filter(item => !item.is_returned)
  return []
}

// 加载数据
async function loadData() {
  if (activeTab.value === 'borrow') {
    await loadBorrowList()
  } else if (activeTab.value === 'pending') {
    await loadPendingReturns()
  } else {
    await loadReturnList()
  }
}

// 加载借用统计
async function loadStatistics() {
  try {
    const res = await request.get('/assets/borrows/statistics/')
    statistics.value = res
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载借用记录
async function loadBorrowList() {
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
      params.borrow_department = filterForm.department
    }
    if (filterForm.user) {
      params.borrow_user = filterForm.user
    }
    if (filterForm.dateRange?.[0]) {
      params.borrow_date_after = filterForm.dateRange[0]
    }
    if (filterForm.dateRange?.[1]) {
      params.borrow_date_before = filterForm.dateRange[1]
    }
    
    const res = await request.get('/assets/borrows/', { params })
    borrowList.value = res?.results || res || []
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载借用记录失败:', error)
    ElMessage.error('加载借用记录失败')
  } finally {
    loading.value = false
  }
}

// 加载待归还清单
async function loadPendingReturns() {
  loading.value = true
  try {
    const res = await request.get('/assets/borrows/pending_returns/', {
      params: {
        filter_type: pendingFilter.value
      }
    })
    pendingReturnList.value = res?.results || res || []
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载待归还清单失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载归还记录
async function loadReturnList() {
  loading.value = true
  try {
    const res = await request.get('/assets/operations/', {
      params: {
        operation_type: 'give_back',
        page: pagination.current,
        page_size: pagination.pageSize
      }
    })
    returnList.value = (res?.results || res || []).map(op => ({
      id: op.id,
      return_no: op.operation_no || `GH-${op.id}`,
      asset_name: op.asset_name,
      asset_code: op.asset_code,
      return_user_name: op.operator_name,
      return_date: op.created_at,
      status: 'completed'
    }))
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载归还记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索可用资产（状态为闲置）
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

// 部门树过滤方法
function filterDepartment(value, data) {
  if (!value) return true
  const searchValue = value.toLowerCase()
  return data.name.toLowerCase().includes(searchValue) || 
         (data.fullPath && data.fullPath.toLowerCase().includes(searchValue))
}

// 加载用户列表
async function loadUsers() {
  try {
    const res = await request.get('/auth/users/', { params: { page_size: 1000 } })
    userOptions.value = res?.results || res || []
  } catch (error) {
    console.error('加载用户失败:', error)
  }
}

// 加载部门树
async function loadDepartments() {
  try {
    const res = await request.get('/organizations/departments/tree/')
    const data = res || []
    departmentOptions.value = addPathToTree(data, '')
  } catch (error) {
    console.error('加载部门失败:', error)
  }
}

// 为部门树添加路径信息
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

function handleTabChange() {
  pagination.current = 1
  loadData()
}

function handleNewBorrow() {
  borrowForm.assets = []
  borrowForm.borrow_user = null
  borrowForm.borrow_department = null
  borrowForm.borrow_date = new Date().toISOString().split('T')[0]
  // 默认预计归还日期为7天后
  const defaultReturn = new Date()
  defaultReturn.setDate(defaultReturn.getDate() + 7)
  borrowForm.expected_return_date = defaultReturn.toISOString().split('T')[0]
  borrowForm.reason = ''
  searchAssets('') // 加载可用资产
  borrowDialogVisible.value = true
}

function handleView(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
}

function handleViewPending(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
}

function handleViewReturn(row) {
  ElMessage.info(`归还单号: ${row.return_no}`)
}

function handleReturnAsset(row) {
  currentRecord.value = row
  returnForm.borrow_id = row.id
  returnForm.asset_ids = getUnreturnedItems(row).map(item => item.asset || item.asset_id)
  returnForm.return_date = new Date().toISOString().split('T')[0]
  returnForm.condition = 'good'
  returnForm.remark = ''
  returnDialogVisible.value = true
}

function handleReturnPending(row) {
  currentRecord.value = row
  returnForm.borrow_id = row.id
  returnForm.asset_ids = row.unreturned_items.map(item => item.asset_id)
  returnForm.return_date = new Date().toISOString().split('T')[0]
  returnForm.condition = 'good'
  returnForm.remark = ''
  returnDialogVisible.value = true
}

function handleReturnFromDetail() {
  viewDialogVisible.value = false
  handleReturnAsset(currentRecord.value)
}

// 点击超期统计卡片
function showOverdue() {
  activeTab.value = 'pending'
  pendingFilter.value = 'overdue'
  loadPendingReturns()
}

// 点击即将到期统计卡片
function showUpcoming() {
  activeTab.value = 'pending'
  pendingFilter.value = 'upcoming'
  loadPendingReturns()
}

async function submitBorrow() {
  try {
    await borrowFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  submitting.value = true
  try {
    const data = {
      borrower: borrowForm.borrow_user,
      borrow_department: borrowForm.borrow_department,
      borrow_date: borrowForm.borrow_date,
      expected_return_date: borrowForm.expected_return_date || null,
      reason: borrowForm.reason,
      items_data: borrowForm.assets.map(assetId => ({ 
        asset: assetId,
        remark: borrowForm.reason || ''
      }))
    }
    
    await request.post('/assets/borrows/', data)
    ElMessage.success('借用成功')
    borrowDialogVisible.value = false
    loadBorrowList()
    loadStatistics()
  } catch (error) {
    console.error('借用失败:', error)
    ElMessage.error('借用失败: ' + (error.response?.data?.detail || error.message))
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
    ElMessage.warning('请选择要归还的资产')
    return
  }
  
  submitting.value = true
  try {
    // 调用归还API
    await request.post(`/assets/borrows/${returnForm.borrow_id}/return_assets/`, {
      asset_ids: returnForm.asset_ids,
      return_date: returnForm.return_date,
      condition: returnForm.condition,
      remark: returnForm.remark
    })
    
    ElMessage.success('归还成功')
    returnDialogVisible.value = false
    loadData()
    loadStatistics()
  } catch (error) {
    console.error('归还失败:', error)
    ElMessage.error('归还失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadBorrowList()
  loadUsers()
  loadDepartments()
  loadStatistics()
})
</script>

<style lang="scss" scoped>
.asset-borrow-container {
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
  
  .stats-row {
    margin-bottom: 20px;
    
    .stat-card {
      cursor: pointer;
      transition: all 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }
      
      :deep(.el-card__body) {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px;
      }
      
      .stat-content {
        .stat-number {
          font-size: 28px;
          font-weight: 600;
          color: #1f2937;
          
          &.text-danger {
            color: #F56C6C;
          }
        }
        
        .stat-label {
          font-size: 14px;
          color: #6b7280;
          margin-top: 4px;
        }
      }
      
      .stat-icon {
        font-size: 40px;
        opacity: 0.6;
      }
    }
  }
  
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
  
  .filter-bar {
    margin-bottom: 16px;
  }
  
  .asset-info {
    line-height: 1.8;
    
    .returned-item {
      color: #909399;
      text-decoration: line-through;
    }
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
  
  .text-danger {
    color: #F56C6C;
    font-weight: 500;
  }
  
  .text-warning {
    color: #E6A23C;
    font-weight: 500;
  }
  
  .overdue-icon {
    color: #F56C6C;
    margin-left: 4px;
  }
  
  .tab-badge {
    :deep(.el-badge__content) {
      margin-left: 4px;
    }
  }
}
</style>
