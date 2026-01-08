<template>
  <div class="asset-transfer-container">
    <el-card class="page-card">
      <template #header>
        <div class="page-header">
          <h2>资产调拨</h2>
          <el-button type="primary" @click="handleNewTransfer">
            <el-icon><Plus /></el-icon>
            新建调拨
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选工具栏 -->
      <div class="list-toolbar">
        <div class="toolbar-search">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索单号、资产名称..."
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
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="调出部门">
              <el-tree-select
                v-model="filterForm.from_department"
                :data="departmentOptions"
                :props="{ value: 'id', label: 'displayName', children: 'children' }"
                placeholder="选择部门"
                check-strictly
                filterable
                clearable
                style="width: 180px"
              />
            </el-form-item>
            <el-form-item label="调入部门">
              <el-tree-select
                v-model="filterForm.to_department"
                :data="departmentOptions"
                :props="{ value: 'id', label: 'displayName', children: 'children' }"
                placeholder="选择部门"
                check-strictly
                filterable
                clearable
                style="width: 180px"
              />
            </el-form-item>
            <el-form-item label="调拨日期">
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
      
      <el-table :data="transferList" style="width: 100%" v-loading="loading">
        <el-table-column prop="transfer_no" label="调拨单号" width="150" />
        <el-table-column label="资产信息" min-width="200">
          <template #default="{ row }">
            <div v-for="item in row.items" :key="item.id" class="asset-info">
              {{ item.asset_name || item.asset?.name }} ({{ item.asset_code || item.asset?.asset_code }})
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="from_department_name" label="调出部门" width="120" />
        <el-table-column prop="to_department_name" label="调入部门" width="120" />
        <el-table-column prop="to_user_name" label="调入人员" width="100" />
        <el-table-column prop="transfer_date" label="调拨日期" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="loadTransferList"
        />
      </div>
    </el-card>
    
    <!-- 新建调拨对话框 -->
    <el-dialog v-model="transferDialogVisible" title="新建调拨" width="900px" destroy-on-close>
      <el-form ref="transferFormRef" :model="transferForm" :rules="transferRules" label-width="100px">
        <!-- 调拨方式选择 -->
        <el-form-item label="调拨方式">
          <el-radio-group v-model="transferForm.transferType" @change="handleTransferTypeChange">
            <el-radio-button value="asset">按资产调拨</el-radio-button>
            <el-radio-button value="user">按人员调拨</el-radio-button>
            <el-radio-button value="department">按部门调拨</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 按资产调拨：选择具体资产 -->
        <el-form-item v-if="transferForm.transferType === 'asset'" label="选择资产" prop="assets">
          <el-select
            v-model="transferForm.assets"
            multiple
            filterable
            remote
            :remote-method="searchAssets"
            :loading="searchingAssets"
            placeholder="请搜索并选择要调拨的资产"
            style="width: 100%"
            @change="handleAssetChange"
          >
            <el-option
              v-for="asset in availableAssets"
              :key="asset.id"
              :label="`${asset.name} (${asset.asset_code})`"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>

        <!-- 按人员调拨：选择人员 -->
        <el-form-item v-if="transferForm.transferType === 'user'" label="选择人员" prop="sourceUser">
          <el-select 
            v-model="transferForm.sourceUser" 
            filterable 
            placeholder="请选择要调拨资产的人员" 
            style="width: 100%"
            @change="loadUserAssets"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <!-- 按部门调拨：选择部门 -->
        <el-form-item v-if="transferForm.transferType === 'department'" label="选择部门" prop="sourceDepartment">
          <el-tree-select
            v-model="transferForm.sourceDepartment"
            :data="departmentOptions"
            :props="{ value: 'id', label: 'displayName', children: 'children' }"
            placeholder="请选择要调拨资产的部门"
            check-strictly
            filterable
            :filter-node-method="filterDepartment"
            style="width: 100%"
            @change="loadDepartmentAssets"
          />
        </el-form-item>

        <!-- 显示已选资产及原信息 -->
        <el-form-item v-if="selectedAssetDetails.length > 0" label="待调拨资产">
          <el-table :data="selectedAssetDetails" border size="small" max-height="250">
            <el-table-column type="selection" width="50" v-if="transferForm.transferType !== 'asset'" />
            <el-table-column prop="name" label="资产名称" min-width="120" />
            <el-table-column prop="asset_code" label="资产编号" width="140" />
            <el-table-column label="原使用人" width="100">
              <template #default="{ row }">
                {{ row.using_user_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="原部门" width="120">
              <template #default="{ row }">
                {{ row.using_department_name || row.manage_department_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="原位置" width="120">
              <template #default="{ row }">
                {{ row.location_name || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="getAssetStatusType(row.status)">{{ row.status_display || row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div class="asset-summary">
            共 {{ selectedAssetDetails.length }} 项资产
          </div>
        </el-form-item>

        <el-divider content-position="left">调拨目标（至少选择一项）</el-divider>

        <!-- 目标选择：人员/部门/位置 三选一或组合 -->
        <el-form-item label="新使用人">
          <el-select 
            v-model="transferForm.to_user" 
            filterable 
            clearable
            placeholder="选择新使用人（可选）" 
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="新部门">
          <el-tree-select
            v-model="transferForm.to_department"
            :data="departmentOptions"
            :props="{ value: 'id', label: 'displayName', children: 'children' }"
            placeholder="选择新部门（可选）"
            check-strictly
            filterable
            clearable
            :filter-node-method="filterDepartment"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="新存放位置">
          <el-tree-select
            v-model="transferForm.to_location"
            :data="locationOptions"
            :props="{ value: 'id', label: 'displayName', children: 'children' }"
            placeholder="选择新存放位置（可选）"
            check-strictly
            filterable
            clearable
            :filter-node-method="filterLocation"
            style="width: 100%"
          />
        </el-form-item>

        <el-divider />

        <el-form-item label="调拨日期" prop="transfer_date">
          <el-date-picker
            v-model="transferForm.transfer_date"
            type="date"
            placeholder="请选择调拨日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="调拨原因">
          <el-input v-model="transferForm.reason" type="textarea" :rows="3" placeholder="请输入调拨原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitTransfer">确认调拨</el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog v-model="viewDialogVisible" title="调拨详情" width="700px">
      <el-descriptions :column="2" border v-if="currentRecord">
        <el-descriptions-item label="调拨单号">{{ currentRecord.transfer_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRecord.status)">{{ getStatusLabel(currentRecord.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="调出部门">{{ currentRecord.from_department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="调入部门">{{ currentRecord.to_department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="调入人员">{{ currentRecord.to_user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="新存放位置">{{ currentRecord.to_location_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="调拨日期">{{ currentRecord.transfer_date }}</el-descriptions-item>
        <el-descriptions-item label="调拨原因">{{ currentRecord.reason || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <h4 style="margin: 16px 0 8px;">调拨资产</h4>
      <el-table :data="currentRecord?.items || []" border size="small">
        <el-table-column prop="asset_name" label="资产名称" />
        <el-table-column prop="asset_code" label="资产编号" width="150" />
        <el-table-column prop="from_user_name" label="原使用人" width="100" />
        <el-table-column prop="from_department_name" label="原部门" width="120" />
        <el-table-column prop="from_location_name" label="原位置" width="120" />
      </el-table>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Plus, Search, Filter, Refresh, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const submitting = ref(false)
const transferDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentRecord = ref(null)
const searchingAssets = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const showAdvanced = ref(false)
const filterForm = reactive({
  status: null,
  from_department: null,
  to_department: null,
  dateRange: null
})

// 列配置
const allColumns = [
  { prop: 'transfer_no', label: '调拨单号' },
  { prop: 'asset_info', label: '资产信息' },
  { prop: 'from_department_name', label: '调出部门' },
  { prop: 'to_department_name', label: '调入部门' },
  { prop: 'to_user_name', label: '调入人员' },
  { prop: 'transfer_date', label: '调拨日期' },
  { prop: 'status', label: '状态' }
]
const visibleColumns = ref(['transfer_no', 'asset_info', 'from_department_name', 'to_department_name', 'to_user_name', 'transfer_date', 'status'])

function toggleAdvanced() {
  showAdvanced.value = !showAdvanced.value
}

function handleSearch() {
  pagination.current = 1
  loadTransferList()
}

function handleReset() {
  searchKeyword.value = ''
  filterForm.status = null
  filterForm.from_department = null
  filterForm.to_department = null
  filterForm.dateRange = null
  pagination.current = 1
  loadTransferList()
}

function resetColumns() {
  visibleColumns.value = ['transfer_no', 'asset_info', 'from_department_name', 'to_department_name', 'to_user_name', 'transfer_date', 'status']
}

function isColumnVisible(prop) {
  return visibleColumns.value.includes(prop)
}

// 监听筛选条件变化
watch(filterForm, () => {
  pagination.current = 1
  loadTransferList()
}, { deep: true })

const transferFormRef = ref()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

const transferList = ref([])
const availableAssets = ref([])
const selectedAssetDetails = ref([])
const departmentOptions = ref([])
const locationOptions = ref([])
const userOptions = ref([])

const transferForm = reactive({
  transferType: 'asset', // asset, user, department
  assets: [],
  sourceUser: null,
  sourceDepartment: null,
  to_user: null,
  to_department: null,
  to_location: null,
  transfer_date: new Date().toISOString().split('T')[0],
  reason: ''
})

const transferRules = {
  assets: [{ 
    validator: (rule, value, callback) => {
      if (transferForm.transferType === 'asset' && (!value || value.length === 0)) {
        callback(new Error('请选择要调拨的资产'))
      } else {
        callback()
      }
    }, 
    trigger: 'change' 
  }],
  sourceUser: [{
    validator: (rule, value, callback) => {
      if (transferForm.transferType === 'user' && !value) {
        callback(new Error('请选择要调拨资产的人员'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }],
  sourceDepartment: [{
    validator: (rule, value, callback) => {
      if (transferForm.transferType === 'department' && !value) {
        callback(new Error('请选择要调拨资产的部门'))
      } else {
        callback()
      }
    },
    trigger: 'change'
  }],
  transfer_date: [{ required: true, message: '请选择调拨日期', trigger: 'change' }]
}

// 状态映射
const statusMap = {
  draft: { label: '草稿', type: 'info' },
  pending: { label: '待审批', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  completed: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'info' }
}

const assetStatusMap = {
  idle: { label: '闲置', type: 'success' },
  in_use: { label: '使用中', type: 'primary' },
  borrowed: { label: '借用中', type: 'warning' },
  maintenance: { label: '维修中', type: 'danger' },
  disposed: { label: '已处置', type: 'info' }
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusLabel(status) {
  return statusMap[status]?.label || status
}

function getAssetStatusType(status) {
  return assetStatusMap[status]?.type || 'info'
}

// 加载调拨记录
async function loadTransferList() {
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
    if (filterForm.from_department) {
      params.from_department = filterForm.from_department
    }
    if (filterForm.to_department) {
      params.to_department = filterForm.to_department
    }
    if (filterForm.dateRange?.[0]) {
      params.transfer_date_after = filterForm.dateRange[0]
    }
    if (filterForm.dateRange?.[1]) {
      params.transfer_date_before = filterForm.dateRange[1]
    }
    
    const res = await request.get('/assets/transfers/', { params })
    transferList.value = res?.results || res || []
    pagination.total = res?.count || 0
  } catch (error) {
    console.error('加载调拨记录失败:', error)
    ElMessage.error('加载调拨记录失败')
  } finally {
    loading.value = false
  }
}

// 搜索资产
async function searchAssets(query) {
  searchingAssets.value = true
  try {
    const res = await request.get('/assets/list/', {
      params: {
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

// 资产选择变化时加载详情
async function handleAssetChange(assetIds) {
  if (!assetIds || assetIds.length === 0) {
    selectedAssetDetails.value = []
    return
  }
  
  try {
    // 获取已选资产的详细信息
    const details = []
    for (const id of assetIds) {
      // 先从已加载列表中查找
      let asset = availableAssets.value.find(a => a.id === id)
      if (!asset) {
        // 如果不在列表中，单独获取
        const res = await request.get(`/assets/list/${id}/`)
        asset = res
      }
      if (asset) {
        details.push(asset)
      }
    }
    selectedAssetDetails.value = details
  } catch (error) {
    console.error('加载资产详情失败:', error)
  }
}

// 按人员加载资产
async function loadUserAssets(userId) {
  if (!userId) {
    selectedAssetDetails.value = []
    return
  }
  
  try {
    const res = await request.get('/assets/list/', {
      params: {
        using_user: userId,
        page_size: 999
      }
    })
    selectedAssetDetails.value = res?.results || res || []
    // 自动设置资产ID列表
    transferForm.assets = selectedAssetDetails.value.map(a => a.id)
  } catch (error) {
    console.error('加载用户资产失败:', error)
    ElMessage.error('加载用户资产失败')
  }
}

// 按部门加载资产
async function loadDepartmentAssets(departmentId) {
  if (!departmentId) {
    selectedAssetDetails.value = []
    return
  }
  
  try {
    const res = await request.get('/assets/list/', {
      params: {
        using_department: departmentId,
        page_size: 999
      }
    })
    selectedAssetDetails.value = res?.results || res || []
    // 自动设置资产ID列表
    transferForm.assets = selectedAssetDetails.value.map(a => a.id)
  } catch (error) {
    console.error('加载部门资产失败:', error)
    ElMessage.error('加载部门资产失败')
  }
}

// 调拨方式变化
function handleTransferTypeChange() {
  // 清空已选数据
  transferForm.assets = []
  transferForm.sourceUser = null
  transferForm.sourceDepartment = null
  selectedAssetDetails.value = []
}

// 部门树过滤方法
function filterDepartment(value, data) {
  if (!value) return true
  const searchValue = value.toLowerCase()
  return data.name.toLowerCase().includes(searchValue) || 
         (data.fullPath && data.fullPath.toLowerCase().includes(searchValue))
}

// 位置树过滤方法
function filterLocation(value, data) {
  if (!value) return true
  const searchValue = value.toLowerCase()
  return data.name.toLowerCase().includes(searchValue) || 
         (data.fullPath && data.fullPath.toLowerCase().includes(searchValue))
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

// 为树形数据添加路径信息
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

// 加载位置树
async function loadLocations() {
  try {
    const res = await request.get('/organizations/locations/tree/')
    const data = res || []
    locationOptions.value = addPathToTree(data, '')
  } catch (error) {
    console.error('加载位置失败:', error)
  }
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

function handleNewTransfer() {
  transferForm.transferType = 'asset'
  transferForm.assets = []
  transferForm.sourceUser = null
  transferForm.sourceDepartment = null
  transferForm.to_user = null
  transferForm.to_department = null
  transferForm.to_location = null
  transferForm.transfer_date = new Date().toISOString().split('T')[0]
  transferForm.reason = ''
  selectedAssetDetails.value = []
  searchAssets('') // 加载资产
  transferDialogVisible.value = true
}

function handleView(row) {
  currentRecord.value = row
  viewDialogVisible.value = true
}

async function submitTransfer() {
  try {
    await transferFormRef.value?.validate()
  } catch (error) {
    return
  }
  
  // 验证至少选择了一个目标
  if (!transferForm.to_user && !transferForm.to_department && !transferForm.to_location) {
    ElMessage.warning('请至少选择一个调拨目标（新使用人、新部门或新位置）')
    return
  }
  
  // 验证资产
  if (selectedAssetDetails.value.length === 0) {
    ElMessage.warning('请选择要调拨的资产')
    return
  }
  
  submitting.value = true
  try {
    // 获取第一个资产的原部门作为调出部门
    const firstAsset = selectedAssetDetails.value[0]
    const fromDepartment = firstAsset?.using_department || firstAsset?.manage_department
    
    const data = {
      from_department: fromDepartment,
      to_department: transferForm.to_department,
      to_user: transferForm.to_user,
      to_location: transferForm.to_location,
      transfer_date: transferForm.transfer_date,
      reason: transferForm.reason,
      items_data: selectedAssetDetails.value.map(asset => ({ 
        asset: asset.id,
        from_user: asset.using_user,
        from_department: asset.using_department || asset.manage_department,
        from_location: asset.location,
        remark: transferForm.reason || ''
      }))
    }
    
    await request.post('/assets/transfers/', data)
    ElMessage.success('调拨成功')
    transferDialogVisible.value = false
    loadTransferList()
  } catch (error) {
    console.error('调拨失败:', error)
    ElMessage.error('调拨失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadTransferList()
  loadDepartments()
  loadLocations()
  loadUsers()
})
</script>

<style lang="scss" scoped>
.asset-transfer-container {
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
  
  .asset-info {
    line-height: 1.8;
  }
  
  .asset-summary {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
  }
  
  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  
  :deep(.el-divider__text) {
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
  }
}
</style>
